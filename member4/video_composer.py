import json
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

def load_vgp(vgp_path):
    with open(vgp_path, "r", encoding="utf-8") as file:
        vgp = json.load(file)

    return vgp
def get_scenes(vgp):
    return vgp["scenes"]

def get_scene_durations(scenes):
    durations = [scene["duration"] for scene in scenes]

    for duration in durations:
        if duration <= 0:
            raise ValueError("Scene duration must be greater than 0")

    return durations

def get_scene_images(job_id, scenes):
    return [
        f"assets/{job_id}/scene_{scene['scene_id']}.png"
        for scene in scenes
    ]

def get_scene_audio(job_id, scenes):
    return [
        f"assets/{job_id}/scene_{scene['scene_id']}.wav"
        for scene in scenes
    ]
    
import os

def validate_assets(image_paths, audio_paths):
    for image_path, audio_path in zip(image_paths, audio_paths):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")

    return True

def create_video(image_paths, audio_paths, durations, output_path, fps=24):
    """
    Create a video from a list of images.

    Parameters:
        image_paths: list of image file paths
        output_path: path where the video will be saved
        duration_per_image: duration of each image in seconds
        fps: video frame rate
    """

    clips = []
    validate_assets(image_paths, audio_paths)

    if len(image_paths) != len(audio_paths):
        raise ValueError("Number of images and audio files must match")

    for image_path, audio_path, duration in zip(image_paths, audio_paths, durations):
        video_clip = ImageClip(image_path).with_duration(duration)
        audio_clip = AudioFileClip(audio_path)
        video_clip = video_clip.with_audio(audio_clip)
        clips.append(video_clip)

    final_video = concatenate_videoclips(clips, method="compose")

    final_video.write_videofile(
        output_path,
        fps=fps
    )

    final_video.close()

    for clip in clips:
        clip.close()

if __name__ == "__main__":

    vgp = load_vgp("../output/JOB_010_vgp.json")

    scenes = get_scenes(vgp)

    images = get_scene_images(vgp["job_id"], scenes)

    durations = get_scene_durations(scenes)

    audio_paths = get_scene_audio(vgp["job_id"], scenes)

    create_video(
        images,
        audio_paths,
        durations,
        "assets/vgp_audio_scene_test.mp4"
    )