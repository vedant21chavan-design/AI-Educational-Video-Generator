import json

from member2.input_adapter import load_member1_input
from member2.decomposer.pipeline import process_topic


INPUT_FILE = "input/JOB_010_input.json"


data = load_member1_input(INPUT_FILE)


print("\nMEMBER 1 INPUT RECEIVED")
print("-----------------------")

print("Job ID:", data["job_id"])
print("Topic:", data["topic"])
print("Domain:", data["domain"])
print(
    "Confidence:",
    data["domain_confidence"]
)


print("\nSTARTING MEMBER 2...\n")


packet = process_topic(
    job_id=data["job_id"],
    topic=data["topic"],
    domain=data["domain"],
    confidence=data["domain_confidence"]
)


output_file = (
    f"output/{data['job_id']}_vgp.json"
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        packet.model_dump(),
        file,
        indent=2,
        ensure_ascii=False
    )


print("\nMEMBER 2 FINISHED")
print("-----------------")
print("Status:", packet.status.value)
print("Output:", output_file)