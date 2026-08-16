import json

from member2.decomposer.llm import generate_content
from member2.decomposer.prompt import SYSTEM_PROMPT
from member2.vgp.schema import Scene


def decompose_topic(topic: str, domain: str):

    prompt = f"""
{SYSTEM_PROMPT}

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

    if not 4 <= len(data["scenes"]) <= 6:
        raise ValueError(
            f"Expected 4-6 scenes, got {len(data['scenes'])}"
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