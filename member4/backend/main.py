from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid

from video_composer import (
    load_vgp,
    get_scenes,
    get_scene_durations,
    get_scene_images,
    get_scene_audio,
    create_video
)


# -----------------------------
# Configuration
# -----------------------------

VGP_PATH = "../output/JOB_010_vgp.json"


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

def prepare_video_data():
    vgp = load_vgp(VGP_PATH)

    scenes = get_scenes(vgp)
    durations = get_scene_durations(scenes)
    images = get_scene_images(vgp["job_id"], scenes)
    audio_paths = get_scene_audio(vgp["job_id"], scenes)

    return images, audio_paths, durations


# -----------------------------
# Background Video Generation
# -----------------------------

def run_video_generation(job_id, topic):
    try:
        jobs[job_id]["status"] = "PROCESSING"

        output_path = f"assets/JOB_010/{job_id}.mp4"

        images, audio_paths, durations = prepare_video_data()

        create_video(
            images,
            audio_paths,
            durations,
            output_path
        )

        jobs[job_id]["status"] = "COMPLETED"
        jobs[job_id]["video_path"] = output_path

    except Exception as e:
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["error"] = str(e)


# -----------------------------
# Test Video Generation
# -----------------------------

def generate_test_video():
    images, audio_paths, durations = prepare_video_data()

    output_path = "assets/JOB_010/backend_test_video.mp4"

    create_video(
        images,
        audio_paths,
        durations,
        output_path
    )

    return output_path


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
    job_id = str(uuid.uuid4())

    # Create initial job record
    jobs[job_id] = {
        "status": "PROCESSING",
        "topic": request.topic
    }

    # Start video generation in background
    background_tasks.add_task(
        run_video_generation,
        job_id,
        request.topic
    )

    # Return immediately
    return {
        "job_id": job_id,
        "status": "PROCESSING",
        "topic": request.topic
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

    video_path = f"assets/JOB_010/{job_id}.mp4"

    import os

    if not os.path.exists(video_path):
        return {
            "error": "Video not found"
        }

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4"
    )

# -----------------------------
# VGP Information Endpoint
# -----------------------------

@app.get("/vgp")
def get_vgp():

    vgp = load_vgp(VGP_PATH)

    return {
        "job_id": vgp["job_id"],
        "topic": vgp["topic"],
        "domain": vgp["domain"],
        "scene_count": len(vgp["scenes"])
    }
