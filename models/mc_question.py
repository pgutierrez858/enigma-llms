from typing import List, Literal

from pydantic import BaseModel, Field


class McQuestion(BaseModel):
    stage_type: Literal['mc-question'] = Field(default='mc-question')
    artifact_name: str
    question: str
    correct_answer: str
    distractors: List[str]


class McQuestionPlan(BaseModel):
    stage_type: Literal['mc-question'] = Field(default='mc-question')
    artifact_name: str
    facts_to_consider: List[str]
    question_style: str
    difficulty: str
    focus: str
    n_answers: int
