from typing import List, Literal

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    description: str


class CharacterIntervention(BaseModel):
    character_name: str
    intervention_text: str


class Narrative(BaseModel):
    stage_type: Literal['narrative'] = Field(default='narrative')
    interventions: List[CharacterIntervention]


class NarrativePlan(BaseModel):
    stage_type: Literal['narrative'] = Field(default='narrative')
    artifact_name: str
    characters_available: List[Character]
    narrative_style: str
    max_interactions: int
    focus: str
