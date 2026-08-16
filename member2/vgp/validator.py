from member2.vgp.states import VGPStatus
from member2.vgp.schema import VGP


ALLOWED_STATES = {
    "CREATED",
    "VALIDATED",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    "RETRY",
    "TIMEOUT",
    "PARTIAL",
    "ABORTED"
}


def validate_vgp(packet: VGP) -> bool:

    # Check job ID
    if not packet.job_id:
        raise ValueError("job_id is required")

    # Check topic
    if not packet.topic:
        raise ValueError("topic is required")

    # Check status
    if packet.status.value not in ALLOWED_STATES:
        raise ValueError(
            f"Invalid status: {packet.status}"
        )

    # Check number of scenes
    if len(packet.scenes) < 1:
        raise ValueError(
            "At least one scene is required"
        )

    if len(packet.scenes) > 6:
        raise ValueError(
            "Maximum 6 scenes are allowed"
        )

    # Check domain
    if packet.domain is None:
        raise ValueError(
            "Domain is required"
        )

    # Check confidence
    if packet.domain_confidence is not None:

        if not 0 <= packet.domain_confidence <= 1:
            raise ValueError(
                "Domain confidence must be between 0 and 1"
            )

    # Check every scene
    for scene in packet.scenes:

        if not scene.title:
            raise ValueError(
                f"Scene {scene.scene_id} has no title"
            )

        if not scene.narration:
            raise ValueError(
                f"Scene {scene.scene_id} has no narration"
            )

        if not scene.visual_prompt:
            raise ValueError(
                f"Scene {scene.scene_id} has no visual prompt"
            )

        if not 3 <= scene.duration <= 30:
            raise ValueError(
                f"Scene {scene.scene_id} has invalid duration"
            )

    return True