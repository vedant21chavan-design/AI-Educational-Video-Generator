import json

from member2.decomposer.pipeline import process_topic


print("\n====================================")
print(" AI EDUCATIONAL VIDEO GENERATOR")
print("====================================\n")


topic = input("Enter educational topic: ").strip()

domain = input(
    "Enter domain (Physics/Chemistry/Biology/Astronomy): "
).strip()

job_id = input(
    "Enter Job ID (example: JOB_004): "
).strip()


if not topic:
    print("ERROR: Topic cannot be empty.")
    exit()

if not domain:
    print("ERROR: Domain cannot be empty.")
    exit()

if not job_id:
    print("ERROR: Job ID cannot be empty.")
    exit()


print("\nStarting Member-2 pipeline...\n")


packet = process_topic(
    job_id=job_id,
    topic=topic,
    domain=domain,
    confidence=1.0
)


filename = f"output/{job_id}_vgp.json"


with open(
    filename,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        packet.model_dump(),
        file,
        indent=2,
        ensure_ascii=False
    )


print("\n====================================")
print("PROCESS COMPLETED")
print("====================================")

print(f"\nVGP saved to:")
print(filename)