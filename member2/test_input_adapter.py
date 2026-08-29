from member2.input_adapter import load_member1_input


data = load_member1_input(
    "Member1_Domain_Classification/JOB_010_output.json"
)


print("\nMEMBER 1 INPUT RECEIVED\n")

print("Job ID:", data["job_id"])
print("Topic:", data["topic"])
print("Domain:", data["domain"])
print(
    "Confidence:",
    data["domain_confidence"]
)