from vgp.schema import VGP
from vgp.states import VGPStatus


packet = VGP(
    job_id="JOB_002",
    topic="Newton's Laws of Motion",
    domain="Physics",
    domain_confidence=0.95
)

print("Initial:", packet.status.value)

packet.change_status(VGPStatus.VALIDATED)
print("After validation:", packet.status.value)

packet.change_status(VGPStatus.PROCESSING)
print("Processing:", packet.status.value)

packet.change_status(VGPStatus.COMPLETED)
print("Final:", packet.status.value)