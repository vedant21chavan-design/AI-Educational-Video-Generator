from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
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
        }
        for scene in scenes
    ]


def create_vgp_for_topic(job_id, topic):
    """Run Member 1 and Member 2 for the topic submitted by the frontend."""
    # These imports are intentionally lazy: they keep the Member 4 API running
    # even when a teammate's local model or LLM dependency is unavailable.
    from Member1_Domain_Classification.classifier import classify_topic
    from member2.decomposer.pipeline import process_topic

    domain, confidence = classify_topic(topic)
    packet = process_topic(
        job_id=job_id,
        topic=topic,
        domain=domain,
        confidence=confidence,
    )

    return packet.model_dump()


# -----------------------------
# Background Video Generation
# -----------------------------

def run_video_generation(job_id, topic):
    try:
        jobs[job_id]["status"] = "CLASSIFYING"
        vgp = create_vgp_for_topic(job_id, topic)

        if vgp["status"] != "COMPLETED":
            errors = "; ".join(vgp.get("errors", []))
            raise RuntimeError(errors or "Member 2 could not create a scene plan.")

        jobs[job_id]["status"] = "GENERATING_MEDIA"
        scenes = vgp["scenes"]
        generated_media = media_pipeline.generate_video(
            job_id,
            convert_vgp_scenes_for_member3(scenes),
        )

        images = [scene["image"] for scene in generated_media["scenes"]]
        audio_paths = [scene["audio"] for scene in generated_media["scenes"]]
        durations = get_scene_durations(scenes)

        jobs[job_id]["status"] = "COMPOSING_VIDEO"
        output_directory = ASSETS_DIR / job_id
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / f"{job_id}.mp4"

        create_video(
            images,
            audio_paths,
            durations,
            str(output_path)
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
        topic
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
