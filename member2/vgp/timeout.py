from member2.vgp.states import VGPStatus
from member2.vgp.state_machine import transition


def handle_timeout(
    current_status: VGPStatus
) -> VGPStatus:

    return transition(
        current_status,
        VGPStatus.TIMEOUT
    )