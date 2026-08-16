from enum import Enum


class ACKStatus(str, Enum):

    ACK = "ACK"
    NACK = "NACK"


class ACKMessage:

    def __init__(
        self,
        job_id: str,
        status: ACKStatus,
        message: str
    ):

        self.job_id = job_id
        self.status = status
        self.message = message

    def to_dict(self):

        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "message": self.message
        }