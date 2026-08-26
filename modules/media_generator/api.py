from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from modules.media_generator.service import generate_educational_video


app = FastAPI(
    title="AI Educational Video Media Generator",
    version="1.0.0"
)


class Scene(BaseModel):
    scene_id: int
    text: str
    image_prompt: str


class VideoRequest(BaseModel):
    scenes: list[Scene]


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "media-generator"
    }


@app.post("/generate-video")
def generate_video_endpoint(request: VideoRequest):

    try:

        scenes = [
            scene.model_dump()
            for scene in request.scenes
        ]

        result = generate_educational_video(scenes)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )