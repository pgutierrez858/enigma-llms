from typing import List, Annotated, Union, Optional

from pydantic import BaseModel, Field

from models.artifact_data import ArtifactData
from models.clue import CluePlan
from models.mc_question import McQuestionPlan
from models.narrative import NarrativePlan, Character

StagePlan = Annotated[Union[CluePlan, McQuestionPlan, NarrativePlan], Field(discriminator="stage_type")]


class AdventurePlan(BaseModel):
    general_description: str
    characters: List[Character] = Field(default=[])
    artifacts_to_find: List[ArtifactData]
    narrative_style: str
    clue_style: str
    question_style: str
    max_narrative_length: int
    answers_per_question: int
    target_audience: str
    difficulty: str
    intention: str
    planned_clues: List[CluePlan] = Field(default=[])
    planned_questions: List[McQuestionPlan] = Field(default=[])
    planned_narratives: List[NarrativePlan] = Field(default=[])
    planned_intro: Optional[NarrativePlan] = Field(default=None)
    planned_outro: Optional[NarrativePlan] = Field(default=None)

