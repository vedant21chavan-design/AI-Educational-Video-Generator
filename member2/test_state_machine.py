from member2.vgp.states import VGPStatus
from member2.vgp.state_machine import transition


current = VGPStatus.CREATED

print("Current:", current.value)


current = transition(
    current,
    VGPStatus.VALIDATED
)

print("Current:", current.value)


current = transition(
    current,
    VGPStatus.PROCESSING
)

print("Current:", current.value)


current = transition(
    current,
    VGPStatus.COMPLETED
)

print("Current:", current.value)