from member2.vgp.ack import ACKMessage, ACKStatus
from member2.vgp.validator import validate_vgp
from member2.vgp.schema import VGP


def process_vgp(packet: VGP) -> ACKMessage:

    try:

        validate_vgp(packet)

        return ACKMessage(
            job_id=packet.job_id,
            status=ACKStatus.ACK,
            message="VGP received and validated successfully"
        )

    except ValueError as error:

        return ACKMessage(
            job_id=packet.job_id,
            status=ACKStatus.NACK,
            message=str(error)
        )