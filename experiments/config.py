from pydantic import BaseModel, Field


class ConfigModel(BaseModel):
    fact_style: str = Field(..., description="Style of extracted facts, e.g., 'Factual, informative and concise'")
    focus: str = Field(..., description="Focus of the extracted facts, like 'Story behind the artwork'")
    n_facts: int = Field(..., description="Number of facts to extract per artifact")

    narrative_style: str = Field(
        ..., description="Style of the game's narrative, e.g., 'Museum treasure hunt'"
    )
    clue_style: str = Field(
        ..., description="Style of the clues, e.g., 'Factual, as in Find the artwork that...'"
    )
    question_style: str = Field(
        ..., description="Style of the questions"
    )
    max_narrative_length: int = Field(..., description="Maximum number of narrative steps")
    answers_per_question: int = Field(..., description="Number of answer choices per question")
    target_audience: str = Field(..., description="Intended audience, e.g., 'High school students visiting the Prado "
                                                  "Museum'")
    difficulty: str = Field(..., description="Difficulty level of the game")
    intention: str = Field(
        ..., description="Primary goal of the experience, like 'Making students enjoy the visit while learning'"
    )
    general_description: str = Field(
        ..., description="General overview of the game and its objectives"
    )
