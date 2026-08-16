from member2.vgp.states import VGPStatus


VALID_TRANSITIONS = {

    VGPStatus.CREATED: {
        VGPStatus.VALIDATED,
        VGPStatus.FAILED
    },

    VGPStatus.VALIDATED: {
        VGPStatus.PROCESSING,
        VGPStatus.FAILED
    },

    VGPStatus.PROCESSING: {
        VGPStatus.COMPLETED,
        VGPStatus.PARTIAL,
        VGPStatus.RETRY,
        VGPStatus.TIMEOUT,
        VGPStatus.FAILED
    },

    VGPStatus.RETRY: {
        VGPStatus.PROCESSING,
        VGPStatus.FAILED
    },

    VGPStatus.PARTIAL: {
        VGPStatus.PROCESSING,
        VGPStatus.COMPLETED,
        VGPStatus.FAILED
    },

    VGPStatus.TIMEOUT: {
        VGPStatus.RETRY,
        VGPStatus.FAILED
    },

    VGPStatus.FAILED: {
        VGPStatus.RETRY,
        VGPStatus.ABORTED
    },

    VGPStatus.COMPLETED: set(),

    VGPStatus.ABORTED: set()
}


def can_transition(
    current_status: VGPStatus,
    new_status: VGPStatus
) -> bool:

    return new_status in VALID_TRANSITIONS.get(
        current_status,
        set()
    )


def transition(
    current_status: VGPStatus,
    new_status: VGPStatus
) -> VGPStatus:

    if not can_transition(current_status, new_status):

        raise ValueError(
            f"Invalid state transition: "
            f"{current_status.value} -> "
            f"{new_status.value}"
        )

    return new_status