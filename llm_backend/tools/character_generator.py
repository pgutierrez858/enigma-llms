from typing import List

from guidance import system, user, assistant, gen
from loguru import logger

from llm_backend.llm_backend import get_model
from llm_backend.tools.regex_utils import character_regex, sentence_regex
from models.narrative import Character


def generate_adventure_characters(n_characters: int,
                                  general_overview: str,
                                  target_audience: str,
                                  intention: str,
                                  narrative_style: str) -> List[Character]:
    logger.debug("Generating Adventure Characters")

    lm = get_model().model

    with system():
        lm += ("You are a game character generator AI. Your task is to create unique character names and descriptions "
               "based on a general overview of the game. Each character should have a distinct personality, role, "
               "and traits that fit the game's setting and tone. Ensure variety and creativity while keeping the "
               "descriptions concise and engaging.\n")
    with user():
        lm += (f"Generate {n_characters} character names and descriptions based on the following game overview. Each "
               f"character should have a unique personality, and role that fit the game's setting and tone.\n\n")
        lm += "Input:\n"
        lm += f"- This is the narrative style of the game: {narrative_style}.\n"
        lm += f"- This is the target audience of the game: {target_audience}.\n"
        lm += f"- This is an overview of the game: {general_overview}.\n"
        lm += f"- This is the intention of the game: {intention}.\n"

    with assistant():
        characters = []
        for i in range(2):
            lm += (f"Character {i + 1}'s Name: "
                   + gen(max_tokens=50, regex=character_regex, list_append=True, name="characters", suffix='\n'))
            logger.debug(f"Generated Character {i + 1} Name: [{lm['characters'][-1]}]")

            lm += (f"Character {i + 1}'s Description: "
                   + gen(max_tokens=150, regex=sentence_regex, list_append=True, name="character_descriptions",
                         suffix='\n'))
            logger.debug(f"Generated Character {i + 1} Description: [{lm['character_descriptions'][-1]}]")
            characters.append(Character(name=lm['characters'][i], description=lm['character_descriptions'][i]))
    return characters
