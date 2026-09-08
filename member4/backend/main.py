from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import json
import sys
import uuid

# Resolve project files independently of the directory used to start Uvicorn.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from member4.video_composer import (
    get_scene_durations,
    create_video
)
from modules.media_generator import media_pipeline


# -----------------------------
# Configuration
# -----------------------------

ASSETS_DIR = PROJECT_ROOT / "assets"

# Member 3's pipeline uses this module setting to decide where to save the
# PNG and WAV files.  Make it an absolute project path for a reliable handoff.
media_pipeline.ASSETS_DIR = str(ASSETS_DIR)


# In-memory job storage
jobs = {}


# -----------------------------
# FastAPI Application
# -----------------------------

app = FastAPI(
    title="AI Educational Video Generator",
    description="Backend API for Member 4",
    version="1.0.0"
)

# Allow the separate HTML/CSS/JavaScript frontend to call this local API.
# This does not change any existing API endpoint or response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Request Model
# -----------------------------

class GenerateRequest(BaseModel):
    topic: str
    duration_preset: str = "medium"  # "short" | "medium" | "long"


# -----------------------------
# Prepare Video Data
# -----------------------------

def convert_vgp_scenes_for_member3(scenes):
    """Map Member 2's VGP schema to Member 3's media-pipeline schema."""
    return [
        {
            "scene_id": scene["scene_id"],
            "text": scene["narration"],
            "image_prompt": scene["visual_prompt"],
            "duration": scene["duration"],
            "title": scene["title"],
        }
        for scene in scenes
    ]


# Member 1's classifier is a closed 4-class model (Biology / Chemistry /
# Earth Science / Physics): given ANY input, softmax always picks one of
# those four with high confidence, even for topics that are not science at
# all (e.g. "chocolate cake recipe"). It has no way to say "none of the
# above". This gate asks the local LLM a direct yes/no question first, so
# clearly out-of-scope topics are rejected instead of silently producing a
# video for them.
TOPIC_GATE_PROMPT = """
You are a strict topic-relevance checker for an educational video generator.

The generator can ONLY produce videos for school-level science topics that
fall inside these four domains: Biology, Chemistry, Earth Science, Physics.

Decide whether the given topic clearly belongs to one of those four domains.
Topics about cooking, sports, coding, history, celebrities, finance, general
small talk, gibberish, or any other non-science subject must be marked as
NOT supported, even if they mention a scientific-sounding word in passing.

Return ONLY valid JSON in exactly one of these two forms, with no other
text and no Markdown:

{"supported": true}
{"supported": false}
"""


def is_supported_science_topic(topic: str) -> bool:
    """Ask the local LLM whether `topic` is in-scope before we spend time
    classifying and generating media for it."""
    from member2.decomposer.llm import generate_content

    prompt = f"{TOPIC_GATE_PROMPT}\nTopic:\n{topic}\n"

    try:
        response = generate_content(prompt)
        data = json.loads(response)
        return bool(data.get("supported", False))
    except Exception:
        # If the gate itself fails (Ollama unreachable, malformed JSON,
        # etc.) fail OPEN: an infrastructure hiccup here shouldn't block a
        # legitimate topic. The domain classifier still runs normally after.
        return True


def create_vgp_for_topic(job_id, topic, duration_preset="medium"):
    """Run Member 1 and Member 2 for the topic submitted by the frontend."""
    # These imports are intentionally lazy: they keep the Member 4 API running
    # even when a teammate's local model or LLM dependency is unavailable.
    from Member1_Domain_Classification.classifier import classify_topic
    from member2.decomposer.pipeline import process_topic

    if not is_supported_science_topic(topic):
        raise ValueError(
            f"'{topic}' does not look like a Biology, Chemistry, Earth "
            f"Science, or Physics topic. This generator only supports "
            f"those four science domains."
        )

    domain, confidence = classify_topic(topic)
    print(
        f"[Member 1] Topic '{topic}' classified as domain={domain!r} "
        f"confidence={confidence:.4f}"
    )
    packet = process_topic(
        job_id=job_id,
        topic=topic,
        domain=domain,
        confidence=confidence,
        duration_preset=duration_preset,
    )

    return packet.model_dump()


# -----------------------------
# Background Video Generation
# -----------------------------

def run_video_generation(job_id, topic, duration_preset="medium"):
    try:
        jobs[job_id]["status"] = "CLASSIFYING"
        vgp = create_vgp_for_topic(job_id, topic, duration_preset=duration_preset)

        if vgp["status"] != "COMPLETED":
            errors = "; ".join(vgp.get("errors", []))
            raise RuntimeError(errors or "Member 2 could not create a scene plan.")

        jobs[job_id]["status"] = "GENERATING_MEDIA"
        scenes = vgp["scenes"]
        generated_media = media_pipeline.generate_video(
            job_id,
            convert_vgp_scenes_for_member3(scenes),
            domain=vgp["domain"],
        )

        images = [scene["image"] for scene in generated_media["scenes"]]
        audio_paths = [scene["audio"] for scene in generated_media["scenes"]]
        durations = get_scene_durations(scenes)
        # Burn each scene's narration onto the video as a caption overlay,
        # since Stable Diffusion cannot render legible text into the image
        # itself.
        captions = [scene["narration"] for scene in scenes]

        jobs[job_id]["status"] = "COMPOSING_VIDEO"
        output_directory = ASSETS_DIR / job_id
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / f"{job_id}.mp4"

        create_video(
            images,
            audio_paths,
            durations,
            str(output_path),
            captions=captions,
        )

        jobs[job_id]["status"] = "COMPLETED"
        jobs[job_id]["video_path"] = str(output_path)
        jobs[job_id]["domain"] = vgp["domain"]
        jobs[job_id]["scene_count"] = len(scenes)

    except Exception as e:
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["error"] = str(e)


# -----------------------------
# Home Endpoint
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "AI Educational Video Generator API is running"
    }


# -----------------------------
# Generate Video Endpoint
# -----------------------------

@app.post("/generate")
def generate_video(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="A topic is required.")

    job_id = str(uuid.uuid4())

    # Create initial job record
    jobs[job_id] = {
        "status": "PROCESSING",
        "topic": topic
    }

    # Start video generation in background
    background_tasks.add_task(
        run_video_generation,
        job_id,
        topic,
        request.duration_preset
    )

    # Return immediately
    return {
        "job_id": job_id,
        "status": "PROCESSING",
        "topic": topic
    }


# -----------------------------
# Job Status Endpoint
# -----------------------------

@app.get("/status/{job_id}")
def get_status(job_id: str):

    if job_id not in jobs:
        return {
            "job_id": job_id,
            "status": "NOT_FOUND"
        }

    return {
        "job_id": job_id,
        **jobs[job_id]
    }
    
@app.get("/video/{job_id}")
def get_video(job_id: str):

    video_path = ASSETS_DIR / job_id / f"{job_id}.mp4"

    if not video_path.exists():
        return {
            "error": "Video not found"
        }

    return FileResponse(
        str(video_path),
        media_type="video/mp4",
        filename=f"{job_id}.mp4"
    )

# -----------------------------
# VGP Information Endpoint
# -----------------------------

@app.get("/vgp")
def get_vgp():
    return {
        "message": "VGPs are created dynamically for each generation request.",
        "active_jobs": len(jobs)
    }
