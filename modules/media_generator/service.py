from modules.media_generator.media_pipeline import generate_video


def generate_educational_video(scenes):
    """
    Public interface for the backend.

    Parameters:
        scenes (list):
            List of scene dictionaries.

            Example:
            {
                "scene_id": 1,
                "text": "The Sun is the center of our solar system.",
                "image_prompt": "Educational illustration of the Sun..."
            }

    Returns:
        dict:
            Generation result containing status and video path.
    """

    if not scenes:
        raise ValueError("At least one scene is required.")

    # Validate scene structure before starting
    for scene in scenes:

        required_fields = [
            "scene_id",
            "text",
            "image_prompt"
        ]

        for field in required_fields:
            if field not in scene:
                raise ValueError(
                    f"Scene {scene.get('scene_id', '?')} "
                    f"is missing required field: {field}"
                )

    # Run existing media pipeline
    video_path = generate_video(scenes)

    return {
        "success": True,
        "video_path": video_path,
        "message": "Educational video generated successfully."
    }


if __name__ == "__main__":

    test_scenes = [
        {
            "scene_id": 1,
            "text": (
                "The solar system consists of the Sun "
                "and all the objects that orbit around it."
            ),
            "image_prompt": (
                "A clean educational illustration of the solar system, "
                "planets arranged around the Sun, "
                "scientific textbook style"
            )
        }
    ]

    result = generate_educational_video(test_scenes)

    print()
    print("=" * 60)
    print("MEDIA SERVICE TEST")
    print("=" * 60)
    print("Success:", result["success"])
    print("Video:", result["video_path"])
    print("Message:", result["message"])
    print("=" * 60)