from member2.vgp.retry import RetryManager
from member2.vgp.states import VGPStatus


retry_manager = RetryManager()


print("Maximum retries:", 3)


current_status = VGPStatus.PROCESSING


for attempt in range(3):

    new_status = retry_manager.retry(
        current_status
    )

    print(
        f"Attempt {attempt + 1}: "
        f"{new_status.value}"
    )

    current_status = VGPStatus.PROCESSING