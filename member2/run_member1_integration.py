import json

from member2.input_adapter import load_member1_input
from member2.decomposer.pipeline import process_topic


INPUT_FILE = "Member1_Domain_Classification/JOB_010_output.json"


# Step 1: Read Member 1 output
data = load_member1_input(INPUT_FILE)

print("\nMEMBER 1 OUTPUT")
print("----------------")
print("Job ID:", data["job_id"])
print("Topic:", data["topic"])
print("Domain:", data["domain"])
print("Confidence:", data["domain_confidence"])


# Step 2: Send Member 1 result to Member 2
print("\nSTARTING MEMBER 2...\n")

packet = process_topic(
    job_id=data["job_id"],
    topic=data["topic"],
    domain=data["domain"],
    confidence=data["domain_confidence"]
)


# Step 3: Save final VGP
output_file = f"output/{data['job_id']}_vgp.json"

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


print("\nINTEGRATION SUCCESS")
print("-------------------")
print("Member 1 → Member 2")
print("Final status:", packet.status.value)
print("Scenes:", len(packet.scenes))
print("Saved:", output_file)