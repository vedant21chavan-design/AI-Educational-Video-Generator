from member2.vgp.ack import ACKMessage, ACKStatus


ack = ACKMessage(
    job_id="JOB_005",
    status=ACKStatus.ACK,
    message="VGP received and accepted"
)


print(ack.to_dict())