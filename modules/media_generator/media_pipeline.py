import os

from modules.media_generator.image.generator import generate_image
from modules.media_generator.tts.generator import generate_tts


# ================================================================
# CONFIGURATION
# ================================================================

ASSETS_DIR = "assets"


# ================================================================
# SCENE MEDIA GENERATION
# ================================================================

def generate_scene_media(job_id, scene):
    """
    Generate image and narration for one scene.

    Expected scene format:

    {
        "scene_id": 1,
        "text": "...",
        "image_prompt": "...",
        "duration": 8
    }

    Output format:

    assets/
        JOB_XXX/
            scene_1.png
            scene_1.wav

    Returns:

    {
        "scene_id": 1,
        "image": "assets/JOB_XXX/scene_1.png",
        "audio": "assets/JOB_XXX/scene_1.wav",
        "duration": 8
    }
    """

    # ------------------------------------------------------------
    # Validate scene
    # ------------------------------------------------------------

    if "scene_id" not in scene:
        raise ValueError("Scene is missing scene_id.")

    if "text" not in scene:
        raise ValueError(
            f"Scene {scene['scene_id']} is missing text."
        )

    if "image_prompt" not in scene:
        raise ValueError(
            f"Scene {scene['scene_id']} is missing image_prompt."
        )

    if "duration" not in scene:
        raise ValueError(
            f"Scene {scene['scene_id']} is missing duration."
        )

    scene_id = scene["scene_id"]
    text = scene["text"]
    image_prompt = scene["image_prompt"]
    duration = scene["duration"]

    print()
    print("=" * 60)
    print(f"GENERATING MEDIA FOR JOB {job_id}")
    print(f"SCENE {scene_id}")
    print("=" * 60)

    # ------------------------------------------------------------
    # Job output directory
    # ------------------------------------------------------------

    job_dir = os.path.join(
        ASSETS_DIR,
        job_id
    )

    os.makedirs(
        job_dir,
        exist_ok=True
    )

    # ------------------------------------------------------------
    # EXACT BACKEND ASSET CONTRACT
    # ------------------------------------------------------------

    image_path = os.path.join(
        job_dir,
        f"scene_{scene_id}.png"
    )

    audio_path = os.path.join(
        job_dir,
        f"scene_{scene_id}.wav"
    )

    print()
    print("Asset directory:")
    print(job_dir)

    print()
    print("Image output:")
    print(image_path)

    print()
    print("Audio output:")
    print(audio_path)

    print()
    print("VGP scene duration:")
    print(f"{duration} seconds")

    # ------------------------------------------------------------
    # Generate image
    # ------------------------------------------------------------

    print()
    print(
        f"[1/2] Generating image for Scene {scene_id}..."
    )

    print(
        f"Prompt: {image_prompt}"
    )

    generated_image = generate_image(
        prompt=image_prompt,
        output_path=image_path
    )

    print()
    print("Image generated:")
    print(generated_image)

    # ------------------------------------------------------------
    # Generate narration
    # ------------------------------------------------------------

    print()
    print(
        f"[2/2] Generating narration for Scene {scene_id}..."
    )

    print(
        f"Text: {text}"
    )

    generated_audio = generate_tts(
        text=text,
        output_path=audio_path
    )

    print()
    print("Audio generated:")
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

    image_size = os.path.getsize(
        image_path
    )

    audio_size = os.path.getsize(
        audio_path
    )

    if image_size == 0:
        raise RuntimeError(
            f"Generated image is empty: {image_path}"
        )

    if audio_size == 0:
        raise RuntimeError(
            f"Generated audio is empty: {audio_path}"
        )

    print()
    print("=" * 60)
    print(f"SCENE {scene_id} MEDIA GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"PNG: {image_path}"
    )

    print(
        f"WAV: {audio_path}"
    )

    print(
        f"Target duration: {duration} seconds"
    )

    print("=" * 60)

    return {
        "scene_id": scene_id,
        "image": image_path,
        "audio": audio_path,
        "duration": duration
    }


# ================================================================
# JOB MEDIA GENERATION
# ================================================================

def generate_video(job_id, scenes):
    """
    Generate all media assets for one VGP job.

    Expected input:

    job_id:
        "JOB_010"

    scenes:

    [
        {
            "scene_id": 1,
            "text": "...",
            "image_prompt": "...",
            "duration": 8
        },
        {
            "scene_id": 2,
            "text": "...",
            "image_prompt": "...",
            "duration": 10
        }
    ]

    Output:

    assets/
        JOB_010/
            scene_1.png
            scene_1.wav
            scene_2.png
            scene_2.wav

    Returns:

        {
            "job_id": "JOB_010",
            "assets_dir": "assets/JOB_010",
            "scenes": [...]
        }
    """

    # ------------------------------------------------------------
    # Validate job ID
    # ------------------------------------------------------------

    if not job_id:
        raise ValueError(
            "No job_id provided."
        )

    if not isinstance(job_id, str):
        raise ValueError(
            "job_id must be a string."
        )

    # ------------------------------------------------------------
    # Validate scenes
    # ------------------------------------------------------------

    if not scenes:
        raise ValueError(
            "No scenes provided to media pipeline."
        )

    print()
    print("=" * 60)
    print("AI EDUCATIONAL VIDEO - MEDIA ASSET PIPELINE")
    print("=" * 60)

    print(
        f"Job ID: {job_id}"
    )

    print(
        f"Number of scenes: {len(scenes)}"
    )

    print(
        f"Assets directory: "
        f"{os.path.join(ASSETS_DIR, job_id)}"
    )

    print()

    generated_scenes = []

    # ------------------------------------------------------------
    # Generate media for every scene
    # ------------------------------------------------------------

    for index, scene in enumerate(
        scenes,
        start=1
    ):

        scene_id = scene.get(
            "scene_id",
            index
        )

        print()
        print("=" * 60)
        print(
            f"[{index}/{len(scenes)}] "
            f"PROCESSING SCENE {scene_id}"
        )
        print("=" * 60)

        result = generate_scene_media(
            job_id=job_id,
            scene=scene
        )

        generated_scenes.append(
            result
        )

    # ------------------------------------------------------------
    # Final asset validation
    # ------------------------------------------------------------

    job_dir = os.path.join(
        ASSETS_DIR,
        job_id
    )

    print()
    print("=" * 60)
    print("VALIDATING JOB ASSETS")
    print("=" * 60)

    for scene in generated_scenes:

        scene_id = scene["scene_id"]

        image_path = scene["image"]
        audio_path = scene["audio"]

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Missing PNG for scene {scene_id}: "
                f"{image_path}"
            )

        if not os.path.exists(audio_path):
            raise FileNotFoundError(
                f"Missing WAV for scene {scene_id}: "
                f"{audio_path}"
            )

        print(
            f"Scene {scene_id}: "
            f"PNG ✓ | WAV ✓"
        )

    # ------------------------------------------------------------
    # Success
    # ------------------------------------------------------------

    print()
    print("=" * 60)
    print("MEDIA ASSET GENERATION SUCCESSFUL!")
    print("=" * 60)

    print(
        f"Job ID: {job_id}"
    )

    print(
        f"Assets: {job_dir}"
    )

    print()

    for scene in generated_scenes:

        print(
            f"Scene {scene['scene_id']}:"
        )

        print(
            f"  PNG: {scene['image']}"
        )

        print(
            f"  WAV: {scene['audio']}"
        )

    print("=" * 60)

    return {
        "job_id": job_id,
        "assets_dir": job_dir,
        "scenes": generated_scenes
    }


# ================================================================
# LOCAL TEST
# ================================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("TESTING MEDIA ASSET PIPELINE")
    print("=" * 60)

    test_job_id = "JOB_010"

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
            ),

            "duration": 8
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
            ),

            "duration": 10
        }

    ]

    try:

        result = generate_video(
            job_id=test_job_id,
            scenes=test_scenes
        )

        print()
        print("=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(
            f"Job: {result['job_id']}"
        )

        print(
            f"Assets: {result['assets_dir']}"
        )

        print("=" * 60)

    except Exception as error:

        print()
        print("=" * 60)
        print("MEDIA ASSET PIPELINE FAILED")
        print("=" * 60)

        print(
            f"Error: {error}"
        )

        print("=" * 60)

        raise