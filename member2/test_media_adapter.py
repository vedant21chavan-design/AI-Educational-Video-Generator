from member2.media_adapter import vgp_to_media_request
from member2.vgp.schema import VGP, Scene


scene1 = Scene(
    scene_id=1,
    title="Newton's First Law",
    explanation="An object remains at rest or in uniform motion unless acted upon by an external force.",
    narration="Newton's First Law explains the idea of inertia.",
    visual_prompt="Educational illustration of a stationary ball and a moving ball, textbook style.",
    duration=10
)

scene2 = Scene(
    scene_id=2,
    title="Newton's Second Law",
    explanation="Force equals mass multiplied by acceleration.",
    narration="Newton's Second Law relates force, mass, and acceleration.",
    visual_prompt="Educational illustration of a person pushing a cart with force and acceleration arrows.",
    duration=10
)


packet = VGP(
    job_id="JOB_MEDIA_TEST",
    topic="Newton's Laws of Motion",
    domain="Physics",
    domain_confidence=0.97,
    scenes=[scene1, scene2]
)


media_request = vgp_to_media_request(packet)


print("\nMEDIA REQUEST\n")
print(media_request)