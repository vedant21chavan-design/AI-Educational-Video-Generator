from pydantic import BaseModel, Field
from typing import List, Optional
from member2.vgp.states import VGPStatus


class Scene(BaseModel):
    scene_id: int
    title: str
    explanation: str
    narration: str
    visual_prompt: str
    duration: int = Field(default=8, ge=3, le=30)


class Metadata(BaseModel):
    language: str = "English"
    created_by: str = "Member2"


class VGP(BaseModel):
    job_id: str
    topic: str

    domain: Optional[str] = None
    domain_confidence: Optional[float] = None

    status: VGPStatus = VGPStatus.CREATED

    scenes: List[Scene] = Field(default_factory=list)

    metadata: Metadata = Field(
        default_factory=Metadata
    )

    errors: List[str] = Field(
        default_factory=list
    )
    def change_status(self, new_status: VGPStatus):

        from member2.vgp.state_machine import transition

        self.status = transition(
            self.status,
            new_status
        )