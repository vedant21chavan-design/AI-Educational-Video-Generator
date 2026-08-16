from member2.vgp.schema import VGP, Scene
from member2.vgp.validator import validate_vgp

# Create a scene that passes the basic Pydantic schema
scene = Scene(
    scene_id=1,
    title="Introduction",
    explanation="Photosynthesis is a biological process.",
    narration="Photosynthesis is the process by which plants make food.",
    visual_prompt="Educational diagram of a green plant receiving sunlight.",
    duration=8
)


# Create an invalid VGP
# The problem here is the WRONG status.
packet = VGP(
    job_id="JOB_INVALID",
    topic="Photosynthesis",
    domain="Biology",
    domain_confidence=0.96,
    status="WRONG_STATUS",
    scenes=[scene]
)


print("\nTesting invalid VGP...\n")


try:

    validate_vgp(packet)

    print("ERROR: Invalid VGP was accepted!")

except ValueError as error:

    print("INVALID VGP SUCCESSFULLY REJECTED")

    print("\nReason:")
    print(error)