from member2.decomposer.decomposer import decompose_topic


test_cases = [
    ("Newton's Laws of Motion", "Physics"),
    ("Chemical Bonding", "Chemistry"),
    ("Solar Eclipse", "Astronomy")
]


for topic, domain in test_cases:

    print("\n" + "=" * 70)
    print(f"TOPIC: {topic}")
    print(f"DOMAIN: {domain}")
    print("=" * 70)

    scenes = decompose_topic(topic, domain)

    print(f"\nGenerated {len(scenes)} scenes\n")

    for scene in scenes:

        print(f"Scene {scene.scene_id}")
        print(f"Title: {scene.title}")
        print(f"Explanation: {scene.explanation}")
        print(f"Narration: {scene.narration}")
        print(f"Visual Prompt: {scene.visual_prompt}")
        print(f"Duration: {scene.duration} seconds")

        print("-" * 50)