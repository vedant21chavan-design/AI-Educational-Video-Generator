import os

from modules.media_generator.image.generator import generate_image
from modules.media_generator.tts.generator import generate_tts
from modules.media_generator.video.assembler import assemble_video


# ================================================================
# CONFIGURATION
# ================================================================

OUTPUT_DIR = "modules/media_generator/output"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 24


# ================================================================
# MEDIA PIPELINE
# ================================================================

def generate_scene_media(scene):
    """
    Generate image and narration for one scene.

    Expected scene format:

    {
        "scene_id": 1,
        "text": "...",
        "image_prompt": "..."
    }

    Returns:

    {
        "scene_id": 1,
        "image": "...",
        "audio": "..."
    }
    """

    scene_id = scene["scene_id"]
    text = scene["text"]
    image_prompt = scene["image_prompt"]

    print()
    print("=" * 60)
    print(f"GENERATING MEDIA FOR SCENE {scene_id}")
    print("=" * 60)

    # ------------------------------------------------------------
    # Scene output directory
    # ------------------------------------------------------------

    scene_dir = os.path.join(
        OUTPUT_DIR,
        f"scene_{scene_id}"
    )

    os.makedirs(
        scene_dir,
        exist_ok=True
    )

    image_path = os.path.join(
        scene_dir,
        "image.png"
    )

    audio_path = os.path.join(
        scene_dir,
        "narration.wav"
    )

    # ------------------------------------------------------------
    # Generate image
    # ------------------------------------------------------------

    print()
    print(f"[1/2] Generating image for Scene {scene_id}...")
    print(f"Prompt: {image_prompt}")

    generated_image = generate_image(
        prompt=image_prompt,
        output_path=image_path
    )

    print()
    print(f"Image generated:")
    print(generated_image)

    # ------------------------------------------------------------
    # Generate narration
    # ------------------------------------------------------------

    print()
    print(f"[2/2] Generating narration for Scene {scene_id}...")
    print(f"Text: {text}")

    generated_audio = generate_tts(
        text=text,
        output_path=audio_path
    )

    print()
    print(f"Audio generated:")
    print(generated_audio)

    # ------------------------------------------------------------
    # Validate generated files
    # ------------------------------------------------------------

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image generation failed for Scene {scene_id}: "
            f"{image_path}"
        )

    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"TTS generation failed for Scene {scene_id}: "
            f"{audio_path}"
        )

    print()
    print(f"Scene {scene_id} media generated successfully!")

    return {
        "scene_id": scene_id,
        "image": image_path,
        "audio": audio_path
    }


# ================================================================
# FULL MEDIA PIPELINE
# ================================================================

def generate_video(scenes):
    """
    Generate complete video from multiple scenes.

    Each scene must contain:

    {
        "scene_id": int,
        "text": str,
        "image_prompt": str
    }

    Returns:
        Path to final video.
    """

    if not scenes:
        raise ValueError(
            "No scenes provided to media pipeline."
        )

    print()
    print("=" * 60)
    print("AI EDUCATIONAL VIDEO - MEDIA PIPELINE")
    print("=" * 60)

    print(f"Number of scenes: {len(scenes)}")
    print()

    generated_scenes = []

    # ------------------------------------------------------------
    # Generate media for every scene
    # ------------------------------------------------------------

    for index, scene in enumerate(
        scenes,
        start=1
    ):

        print()
        print("=" * 60)
        print(
            f"[{index}/{len(scenes)}] "
            f"PROCESSING SCENE {scene['scene_id']}"
        )
        print("=" * 60)

        result = generate_scene_media(
            scene
        )

        generated_scenes.append(
            result
        )

    # ------------------------------------------------------------
    # Create video output directory
    # ------------------------------------------------------------

    video_dir = os.path.join(
        OUTPUT_DIR,
        "videos"
    )

    os.makedirs(
        video_dir,
        exist_ok=True
    )

    final_video_path = os.path.join(
        video_dir,
        "final_video.mp4"
    )

    # ------------------------------------------------------------
    # Assemble video
    # ------------------------------------------------------------

    print()
    print("=" * 60)
    print("ASSEMBLING FINAL VIDEO")
    print("=" * 60)

    print(
        f"Scenes ready for assembly: "
        f"{len(generated_scenes)}"
    )

    final_video = assemble_video(
        scenes=generated_scenes,
        output_path=final_video_path,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        fps=DEFAULT_FPS
    )

    # ------------------------------------------------------------
    # Final validation
    # ------------------------------------------------------------

    if not os.path.exists(final_video):
        raise FileNotFoundError(
            "Final video was not generated."
        )

    print()
    print("=" * 60)
    print("COMPLETE MEDIA PIPELINE SUCCESSFUL!")
    print("=" * 60)

    print(
        f"Final video: {final_video}"
    )

    print("=" * 60)

    return final_video


# ================================================================
# TEST
# ================================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("TESTING COMPLETE MEDIA PIPELINE")
    print("=" * 60)

    test_scenes = [

        {
            "scene_id": 1,

            "text": (
                "The solar system consists of the Sun "
                "and all the objects that orbit around it."
            ),

            "image_prompt": (
                "A clean educational illustration of "
                "the solar system, planets arranged "
                "around the Sun, scientific textbook "
                "style, clear labels, clean composition, "
                "educational diagram"
            )
        },

        {
            "scene_id": 2,

            "text": (
                "The solar system contains eight planets "
                "that orbit the Sun in predictable paths."
            ),

            "image_prompt": (
                "A clean educational illustration showing "
                "the eight planets orbiting the Sun, "
                "scientific textbook diagram, labeled "
                "planets, clear educational composition"
            )
        }

    ]

    try:

        result = generate_video(
            test_scenes
        )

        print()
        print("=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Video: {result}")
        print("=" * 60)

    except Exception as error:

        print()
        print("=" * 60)
        print("MEDIA PIPELINE FAILED")
        print("=" * 60)
        print(f"Error: {error}")
        print("=" * 60)

        raise