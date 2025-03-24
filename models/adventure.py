from typing import List, Union, Annotated

from pydantic import BaseModel, Field

from models.artifact_data import ArtifactData
from models.clue import Clue
from models.mc_question import McQuestion
from models.narrative import Character, Narrative

Stage = Annotated[Union[Clue, McQuestion, Narrative], Field(discriminator="stage_type")]


class Adventure(BaseModel):
    characters: List[Character] = Field(default=[], description="List of characters in the adventure's narrative.")
    stages: List[Stage] = Field(default=[], description="List of sequential stages comprising the adventure.")
    artifacts: List[ArtifactData] = Field(default=[], description="List of artifacts that can be referenced in the "
                                                                  "adventure.")

    def try_add_character(self, character: Character) -> bool:
        if self.characters.count(character) == 0:
            self.characters.append(character)
            return True
        return False

    def try_add_artifact(self, new_artifact) -> bool:
        if next((artifact for artifact in self.artifacts if new_artifact.name == artifact.name), None) is None:
            self.artifacts.append(new_artifact)
            return True
        return False

    def try_add_stage_at_position(self, stage, pos) -> bool:
        if 0 <= pos < len(self.stages) + 1:
            self.stages.insert(pos, stage)
            return True
        return False
