from member2.vgp.schema import VGP, Scene
from member2.vgp.validator import validate_vgp

# Create one educational scene
scene = Scene(
    scene_id=1,
    title="Introduction to Photosynthesis",
    explanation="Photosynthesis is the process by which green plants make food using sunlight.",
    narration="Photosynthesis is the process by which green plants make their food using sunlight.",
    visual_prompt="Educational diagram of a green plant receiving sunlight, showing leaves and sunlight.",
    duration=8
)


# Create the VGP packet
packet = VGP(
    job_id="JOB_001",
    topic="Photosynthesis",
    domain="Biology",
    domain_confidence=0.96,
    status="CREATED",
    scenes=[scene]
)


# Display the VGP
print("\nVGP PACKET CREATED\n")

print(packet.model_dump_json(indent=2))
print("\nVALIDATING VGP...\n")

if validate_vgp(packet):
    print("VGP VALIDATION SUCCESSFUL")