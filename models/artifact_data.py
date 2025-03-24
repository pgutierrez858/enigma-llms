from typing import List

from pydantic import BaseModel


class ArtifactData(BaseModel):
    name: str
    description: str
    facts: List[str]
