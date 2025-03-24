from guidance import system, user, assistant, gen
from loguru import logger

from llm_backend.llm_backend import get_model
from llm_backend.tools.regex_utils import sentence_regex, sentence_stop_regex
from models.clue import Clue


def generate_clue_to_artifact(artifact_name: str,
                              artifact_description: str,
                              clue_style: str,
                              difficulty: str,
                              focus: str) -> Clue:
    logger.debug("Generating Clue to Artifact")

    lm = get_model().model

    with system():
        lm += ("You are a treasure hunt clue generator AI. Your task is to create single-sentence clues that lead "
               "players to a specific artifact without explicitly naming it. Each clue should be based on details "
               "from the artifact’s description and encourage players to think critically. The clues should be "
               "engaging, slightly cryptic, and thematically appropriate for the artifact’s nature and setting.\n")

    with user():
        lm += (f"Generate a treasure hunt clue based on the following artifact description. Each clue should be a "
               f"single sentence long, subtly guiding players toward the artifact without explicitly naming it.\n\n")

        lm += "Input:\n"
        lm += f"- Artifact on which to generate clue: {artifact_name}.\n"
        lm += f"- Text: {artifact_description}\n"
        lm += f"- Clue should have difficulty:{difficulty}.\n"
        lm += f"- Clue must be exactly a line long and follow this style: {clue_style}.\n"
        lm += f"- Keep the focus on: {focus}.\n"

    with assistant():
        lm += 'Clue: ' + gen(max_tokens=150,
                             regex=sentence_regex,
                             stop_regex=sentence_stop_regex,
                             name='clue',
                             suffix='\n')
        logger.debug(f"Created clue: [{lm['clue']}]")
        clue = Clue(artifact_name=artifact_name, text=lm['clue'])
    return clue
