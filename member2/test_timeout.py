from member2.vgp.timeout import handle_timeout
from member2.vgp.states import VGPStatus


current_status = VGPStatus.PROCESSING


new_status = handle_timeout(
    current_status
)


print("Before:", current_status.value)
print("After:", new_status.value)