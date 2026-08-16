from member2.vgp.protocol import process_vgp
from member2.vgp.schema import VGP


# Intentionally invalid VGP
packet = VGP(
    job_id="JOB_007",
    topic="",
    domain="Physics",
    domain_confidence=0.97
)


result = process_vgp(packet)

print(result.to_dict())