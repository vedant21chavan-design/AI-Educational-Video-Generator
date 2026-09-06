import json

from member2.decomposer.llm import generate_content
from member2.decomposer.prompt import build_system_prompt
from member2.vgp.schema import Scene


def decompose_topic(topic: str, domain: str, scene_count: int = 5, words_per_scene: int = 30):

    system_prompt = build_system_prompt(scene_count, words_per_scene)

    prompt = f"""
{system_prompt}

Topic:
{topic}

Domain:
{domain}

Generate the educational video scenes now.
"""

    response = generate_content(prompt)

    data = json.loads(response)
    if "scenes" not in data:
        raise ValueError("LLM response does not contain scenes")

    # LLMs only approximate a requested scene count, so accept a small
    # tolerance around the target rather than requiring an exact match -
    # an off-by-one shouldn't burn a retry attempt over what's ultimately
    # just a rough length preference.
    min_scenes = max(scene_count - 1, 3)
    max_scenes = scene_count + 1
    if not min_scenes <= len(data["scenes"]) <= max_scenes:
        raise ValueError(
            f"Expected {min_scenes}-{max_scenes} scenes "
            f"(target {scene_count}), got {len(data['scenes'])}"
        )

    scenes = []

    for item in data["scenes"]:

        scene = Scene(
            scene_id=item["scene_id"],
            title=item["title"],
            explanation=item["explanation"],
            narration=item["narration"],
            visual_prompt=item["visual_prompt"],
            duration=item["duration"]
        )

        scenes.append(scene)

    return scenes
