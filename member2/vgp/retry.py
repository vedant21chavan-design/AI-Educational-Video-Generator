from member2.vgp.states import VGPStatus
from member2.vgp.state_machine import transition


MAX_RETRIES = 3


class RetryManager:

    def __init__(self):
        self.attempts = 0

    def should_retry(self) -> bool:
        return self.attempts < MAX_RETRIES

    def retry(self, current_status: VGPStatus):

        if not self.should_retry():
            return VGPStatus.FAILED

        self.attempts += 1

        return transition(
            current_status,
            VGPStatus.RETRY
        )

    def reset(self):
        self.attempts = 0