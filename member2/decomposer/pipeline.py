from member2.decomposer.decomposer import decompose_topic
from member2.vgp.schema import VGP
from member2.vgp.validator import validate_vgp
from member2.vgp.states import VGPStatus
from member2.vgp.protocol import process_vgp
from requests.exceptions import Timeout, RequestException
from member2.vgp.retry import RetryManager


def process_topic(
    job_id: str,
    topic: str,
    domain: str,
    confidence: float
):

    # 1. Create VGP
    packet = VGP(
        job_id=job_id,
        topic=topic,
        domain=domain,
        domain_confidence=confidence
    )

    print("VGP CREATED")

    # 2. Move to processing
    packet.change_status(VGPStatus.VALIDATED)
    packet.change_status(VGPStatus.PROCESSING)

    print("VGP PROCESSING")

    # 3. Generate scenes using local LLM
    print("CONCEPT DECOMPOSITION STARTED")
    retry_manager = RetryManager()
    scenes = None
    while retry_manager.should_retry():
     try:
        attempt_number = retry_manager.attempts + 1
        print(
            f"LLM ATTEMPT {attempt_number}/3"
        )
        scenes = decompose_topic(
            topic,
            domain
        )
        break
     except Timeout:
        print("LLM TIMEOUT")
        retry_manager.retry(
            VGPStatus.PROCESSING
        )
     except RequestException as error:
        print(
            f"LLM REQUEST ERROR: {error}"
        )
        retry_manager.retry(
            VGPStatus.PROCESSING
        )
     except Exception as error:
        print(
            f"LLM ERROR: {error}"
        )
        retry_manager.retry(
            VGPStatus.PROCESSING
        )
    if scenes is None:
     packet.change_status(
        VGPStatus.FAILED
     )
     packet.errors.append(
        "LLM failed after maximum retries"
     )
     print("VGP FAILED")
     return packet
    print(
     f"GENERATED {len(scenes)} SCENES"
    )
    # 4. Add scenes to VGP
    packet.scenes = scenes

    # 5. Validate and generate ACK/NACK
    ack_message = process_vgp(packet)

    print(
     f"PROTOCOL: {ack_message.status.value}"
    )

    print(
     f"PROTOCOL MESSAGE: {ack_message.message}"
    )

    if ack_message.status.value == "NACK":
     packet.change_status(VGPStatus.FAILED)
     return packet

    # 6. Complete
    packet.change_status(VGPStatus.COMPLETED)

    print("VGP COMPLETED")

    return packet