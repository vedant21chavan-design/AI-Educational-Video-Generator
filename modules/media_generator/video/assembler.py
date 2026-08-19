import os
import re

try:
    # MoviePy 2.x
    from moviepy import (
        ImageClip,
        AudioFileClip,
        concatenate_videoclips
    )
except ImportError:
    # MoviePy 1.x fallback
    from moviepy.editor import (
        ImageClip,
        AudioFileClip,
        concatenate_videoclips
    )


DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 24


# ================================================================
# SCENE DISCOVERY
# ================================================================

def discover_scenes(output_directory):
    """
    Automatically discover all scene folders.

    Expected structure:

        output/
        ├── scene_1/
        │   ├── image.png
        │   └── narration.wav
        │
        ├── scene_2/
        │   ├── image.png
        │   └── narration.wav
        │
        └── scene_3/
            ├── image.png
            └── narration.wav

    Returns:
        list: List of scene dictionaries.
    """

    if not os.path.exists(output_directory):
        raise FileNotFoundError(
            f"Output directory not found: {output_directory}"
        )

    scenes = []

    for folder_name in os.listdir(output_directory):

        folder_path = os.path.join(
            output_directory,
            folder_name
        )

        # Only process directories named scene_<number>
        match = re.fullmatch(
            r"scene_(\d+)",
            folder_name,
            re.IGNORECASE
        )

        if not match:
            continue

        scene_id = int(match.group(1))

        image_path = os.path.join(
            folder_path,
            "image.png"
        )

        audio_path = os.path.join(
            folder_path,
            "narration.wav"
        )

        scenes.append(
            {
                "scene_id": scene_id,
                "image": image_path,
                "audio": audio_path
            }
        )

    # Sort scenes numerically
    scenes.sort(
        key=lambda scene: scene["scene_id"]
    )

    return scenes


# ================================================================
# VIDEO ASSEMBLER
# ================================================================

def assemble_video(
    scenes,
    output_path,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    fps=DEFAULT_FPS
):
    """
    Assemble multiple image + narration pairs
    into one MP4 video.

    Parameters:
        scenes (list):
            List of scene dictionaries:

            {
                "scene_id": int,
                "image": str,
                "audio": str
            }

        output_path (str):
            Path where final MP4 is saved.

        width (int):
            Output video width.

        height (int):
            Output video height.

        fps (int):
            Output video frame rate.

    Returns:
        str:
            Path of generated video.
    """

    if not scenes:
        raise ValueError(
            "No scenes were provided."
        )

    print("=" * 60)
    print("VIDEO ASSEMBLER")
    print("=" * 60)

    print(
        f"Number of scenes: {len(scenes)}"
    )

    print(
        f"Resolution: {width}x{height}"
    )

    print(
        f"FPS: {fps}"
    )

    print()

    video_clips = []
    audio_clips = []

    try:

        # --------------------------------------------------------
        # PROCESS EACH SCENE
        # --------------------------------------------------------

        for index, scene in enumerate(
            scenes,
            start=1
        ):

            scene_id = scene.get(
                "scene_id",
                index
            )

            image_path = scene.get(
                "image"
            )

            audio_path = scene.get(
                "audio"
            )

            print(
                f"[{index}/{len(scenes)}] "
                f"Processing Scene {scene_id}"
            )

            # ----------------------------------------------------
            # VALIDATE PATHS
            # ----------------------------------------------------

            if not image_path:
                raise ValueError(
                    f"Scene {scene_id} "
                    f"does not contain an image path."
                )

            if not audio_path:
                raise ValueError(
                    f"Scene {scene_id} "
                    f"does not contain an audio path."
                )

            if not os.path.exists(image_path):
                raise FileNotFoundError(
                    f"Image file not found: "
                    f"{image_path}"
                )

            if not os.path.exists(audio_path):
                raise FileNotFoundError(
                    f"Audio file not found: "
                    f"{audio_path}"
                )

            print(
                f"  Image: {image_path}"
            )

            print(
                f"  Audio: {audio_path}"
            )

            # ----------------------------------------------------
            # LOAD AUDIO
            # ----------------------------------------------------

            audio_clip = AudioFileClip(
                audio_path
            )

            audio_duration = (
                audio_clip.duration
            )

            print(
                f"  Narration duration: "
                f"{audio_duration:.2f} seconds"
            )

            # ----------------------------------------------------
            # CREATE IMAGE CLIP
            # ----------------------------------------------------

            image_clip = ImageClip(
                image_path
            )

            # Resize image to target resolution
            image_clip = image_clip.resized(
                new_size=(
                    width,
                    height
                )
            )

            # Keep image visible for exactly
            # as long as the narration
            image_clip = image_clip.with_duration(
                audio_duration
            )

            # Attach narration
            image_clip = image_clip.with_audio(
                audio_clip
            )

            video_clips.append(
                image_clip
            )

            audio_clips.append(
                audio_clip
            )

            print(
                f"  Scene {scene_id} prepared."
            )

            print()

        # --------------------------------------------------------
        # COMBINE SCENES
        # --------------------------------------------------------

        print(
            "Combining scene clips..."
        )

        final_video = concatenate_videoclips(
            video_clips,
            method="compose"
        )

        # --------------------------------------------------------
        # CREATE OUTPUT DIRECTORY
        # --------------------------------------------------------

        output_directory = os.path.dirname(
            output_path
        )

        if output_directory:
            os.makedirs(
                output_directory,
                exist_ok=True
            )

        # --------------------------------------------------------
        # RENDER FINAL VIDEO
        # --------------------------------------------------------

        print()
        print(
            "Rendering final video..."
        )

        print(
            f"Output: {output_path}"
        )

        print()

        final_video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac"
        )

        print()

        print("=" * 60)
        print(
            "VIDEO GENERATED SUCCESSFULLY!"
        )
        print("=" * 60)

        print(
            f"Saved to: {output_path}"
        )

        print(
            f"Duration: "
            f"{final_video.duration:.2f} seconds"
        )

        print("=" * 60)

        final_video.close()

        return output_path

    finally:

        # --------------------------------------------------------
        # CLEANUP
        # --------------------------------------------------------

        for clip in video_clips:

            try:
                clip.close()

            except Exception:
                pass

        for clip in audio_clips:

            try:
                clip.close()

            except Exception:
                pass


# ================================================================
# TEST / ENTRY POINT
# ================================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "TESTING VIDEO ASSEMBLER"
    )
    print("=" * 60)
    print()

    # ------------------------------------------------------------
    # Output directories
    # ------------------------------------------------------------

    output_root = (
        "modules/media_generator/output"
    )

    video_output_directory = os.path.join(
        output_root,
        "videos"
    )

    output_path = os.path.join(
        video_output_directory,
        "final_video.mp4"
    )

    # ------------------------------------------------------------
    # Automatically discover scenes
    # ------------------------------------------------------------

    print(
        "Discovering scenes..."
    )

    scenes = discover_scenes(
        output_root
    )

    print(
        f"Discovered {len(scenes)} scene(s)."
    )

    print()

    if not scenes:

        raise RuntimeError(
            "No scene folders found."
        )

    # ------------------------------------------------------------
    # Display discovered scenes
    # ------------------------------------------------------------

    for scene in scenes:

        print(
            f"Scene {scene['scene_id']}:"
        )

        print(
            f"  Image: {scene['image']}"
        )

        print(
            f"  Audio: {scene['audio']}"
        )

        print()

    # ------------------------------------------------------------
    # Assemble video
    # ------------------------------------------------------------

    assemble_video(
        scenes=scenes,
        output_path=output_path,
        width=1280,
        height=720,
        fps=24
    )