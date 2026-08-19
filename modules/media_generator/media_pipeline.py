import os
import sys


# --------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# --------------------------------------------------
# MEDIA GENERATORS
# --------------------------------------------------

from modules.media_generator.image.generator import generate_image
from modules.media_generator.tts.generator import generate_tts


# --------------------------------------------------
# OUTPUT DIRECTORY
# --------------------------------------------------

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "modules",
    "media_generator",
    "output"
)


# --------------------------------------------------
# GENERATE SCENE MEDIA
# --------------------------------------------------

def generate_scene_media(scene_id, image_prompt, narration_text):
    """
    Generate all media required for a single educational
    video scene.

    Parameters:
        scene_id (int or str):
            Unique identifier for the scene.

        image_prompt (str):
            Prompt used for image generation.

        narration_text (str):
            Text used for speech generation.

    Returns:
        dict:
            Paths of generated image and audio files.
    """

    print("\n" + "=" * 60)
    print(f"Generating media for Scene {scene_id}")
    print("=" * 60)

    # --------------------------------------------------
    # SCENE OUTPUT DIRECTORY
    # --------------------------------------------------

    scene_dir = os.path.join(
        OUTPUT_DIR,
        f"scene_{scene_id}"
    )

    os.makedirs(
        scene_dir,
        exist_ok=True
    )

    # --------------------------------------------------
    # IMAGE GENERATION
    # --------------------------------------------------

    image_path = os.path.join(
        scene_dir,
        "image.png"
    )

    print("\n[1/2] Generating image...")

    generate_image(
        image_prompt,
        image_path
    )

    # --------------------------------------------------
    # TTS GENERATION
    # --------------------------------------------------

    audio_path = os.path.join(
        scene_dir,
        "narration.wav"
    )

    print("\n[2/2] Generating narration...")

    generate_tts(
        narration_text,
        audio_path
    )

    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    result = {
        "scene_id": scene_id,
        "image": image_path,
        "audio": audio_path
    }

    print("\n" + "=" * 60)
    print(f"Scene {scene_id} media generated successfully!")
    print("=" * 60)

    print("Image :", image_path)
    print("Audio :", audio_path)

    return result


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    test_scene_id = 1

    test_image_prompt = (
        "A clean educational illustration of the solar system, "
        "planets arranged around the Sun, scientific textbook style, "
        "clear labels, clean composition, educational diagram"
    )

    test_narration = (
        "The solar system consists of the Sun and all the objects "
        "that orbit around it. These include eight planets, dwarf "
        "planets, moons, asteroids, and comets."
    )

    result = generate_scene_media(
        test_scene_id,
        test_image_prompt,
        test_narration
    )

    print("\nFinal result:")
    print(result)