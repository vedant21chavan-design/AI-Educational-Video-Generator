import json

from member2.decomposer.pipeline import process_topic


packet = process_topic(
    job_id="JOB_003",
    topic="Newton's Laws of Motion",
    domain="Physics",
    confidence=0.97
)


print("\nFINAL VGP\n")

print(packet.model_dump_json(indent=2))
with open(
    "output/JOB_003_vgp.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        packet.model_dump(),
        file,
        indent=2,
        ensure_ascii=False
    )


print("\nVGP FILE SAVED:")
print("output/JOB_003_vgp.json")