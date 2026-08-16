from member2.input_adapter import load_member1_input


data = load_member1_input(
    "input/JOB_010_input.json"
)


print("\nMEMBER 1 INPUT RECEIVED\n")

print("Job ID:", data["job_id"])
print("Topic:", data["topic"])
print("Domain:", data["domain"])
print(
    "Confidence:",
    data["domain_confidence"]
)