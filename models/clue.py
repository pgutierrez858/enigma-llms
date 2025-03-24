from typing import Literal, List

from pydantic import BaseModel, Field


class Clue(BaseModel):
    stage_type: Literal['clue'] = Field(default='clue')
    artifact_name: str
    text: str


class CluePlan(BaseModel):
    stage_type: Literal['clue'] = Field(default='clue')
    artifact_name: str
    facts_to_consider: List[str]
    clue_style: str
    difficulty: str
    focus: str
