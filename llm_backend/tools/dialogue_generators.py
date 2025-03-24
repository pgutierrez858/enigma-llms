from typing import List

from guidance import guidance, assistant, gen, select, user, system, models
from loguru import logger

from llm_backend.llm_backend import get_model
from llm_backend.tools.dialogue_summarizer import summarize
from llm_backend.tools.regex_utils import sentence_regex, sentence_stop_regex
from models.narrative import Character, Narrative, CharacterIntervention


@guidance
def create_dialogue_from_input(lm: models.Model,
                               available_characters: List[Character],
                               max_interactions: int):
    with assistant():
        j = 0
        while j < max_interactions:
            if j > 0:
                aux_lm = lm
                aux_lm += (f"Does this conversation already fit the input?: "
                           + select(['Yes', 'No'], name='continue'))
                if aux_lm['continue'] == 'Yes':
                    logger.debug("Decided to end the dialogue before reaching the maximum number of interactions")
                    break
            lm += ("Next Speaker: " + select([c.name for c in available_characters], list_append=True, name='speakers')
                   + "\n")
            lm += ("Speaker Text: " + gen(max_tokens=100,
                                          regex=sentence_regex,
                                          stop_regex=sentence_stop_regex,
                                          list_append=True,
                                          name='speaker_texts',
                                          suffix='\n'))
            logger.debug(f"{lm['speakers'][-1]}: {lm['speaker_texts'][-1]}")
            j += 1
    return lm


def create_narrative_stage_from_llm(llm: models.Model) -> Narrative:
    narrative = Narrative(interventions=[])
    for speaker, text in zip(llm['speakers'], llm['speaker_texts']):
        narrative.interventions.append(CharacterIntervention(character_name=speaker, intervention_text=text))
    return narrative


def create_introduction_narrative(available_characters: List[Character],
                                  max_interactions: int,
                                  narrative_style: str,
                                  focus: str) -> Narrative:
    logger.debug(f"Creating introductory narrative block.")

    lm = get_model().model

    with system():
        lm += ("You are a game dialogue generator AI. Your task is to create the starting dialogue of a story based "
               "on a given set of characters and setting. The dialogue should introduce the characters naturally, "
               "establish the tone, and set up the initial scenario in an engaging way. Avoid summarizing "
               "events—focus solely on crafting an immersive opening conversation that draws the player into the "
               "story.\n")
    with user():
        lm += ("Generate the opening dialogue for a story based on the following characters and setting. The dialogue "
               "should introduce the characters naturally, establish the tone, and set up the scenario without "
               "summarizing events. Keep it immersive and engaging.\n\n")
        lm += "Input:\n"
        lm += f"- You should focus on: {focus}\n"
        lm += f"- You should follow this style: {narrative_style}\n"
        lm += f"- Use the following characters:\n"
        for i, character in enumerate(available_characters):
            lm += f"{character.name}: {character.description}\n"
        lm += f"- Use no more than {max_interactions} interactions.\n"
        lm += "- Keep interactions simple and easy to follow.\n"
        lm += "- Each interaction must be exactly a line long.\n"

    lm += create_dialogue_from_input(available_characters=available_characters, max_interactions=max_interactions)
    return create_narrative_stage_from_llm(lm)


def create_ending_narrative(available_characters: List[Character],
                            max_interactions: int,
                            narrative_style: str,
                            focus: str,
                            narrative_before: str) -> Narrative:
    logger.debug(f"Creating final narrative block.")

    lm = get_model().model

    # generate summary of story until now
    # summary = summarize(narrative_before)
    summary = narrative_before

    with system():
        lm += ("You are a game dialogue generator AI. Your task is to create the final dialogue of a story based on a "
               "given summary of events so far. The dialogue should provide a satisfying conclusion, acknowledge the "
               "player's journey, and celebrate their success. Ensure that the conversation naturally reflects the "
               "resolution of the story, offering closure while maintaining the characters' voices and tone. The "
               "dialogue should feel rewarding and immersive, avoiding unnecessary exposition.\n")
    with user():
        lm += (f"Using the final narrative focus, generate an engaging ending dialogue for the game. It should "
               f"congratulate the player, wrap up the story, and provide a sense of accomplishment.\n\n")
        lm += "Input:\n"
        lm += f"- This is a summary of the story until now:\n{summary}\n"
        lm += f"- You should focus on: {focus}\n"
        lm += f"- You should follow this style: {narrative_style}\n"
        lm += f"- Use the following characters:\n"
        for i, character in enumerate(available_characters):
            lm += f"{character.name}: {character.description}\n"
        lm += f"- Use no more than {max_interactions} interactions.\n"
        lm += "- Keep interactions simple and easy to follow.\n"
        lm += "- Each interaction must be exactly a line long.\n"

    lm += create_dialogue_from_input(available_characters=available_characters, max_interactions=max_interactions)
    return create_narrative_stage_from_llm(lm)


def create_narrative_block_before_artifact(narrative_before: str,
                                           clue_focus: str,
                                           available_characters: List[Character],
                                           max_interactions: int,
                                           narrative_style: str,
                                           focus: str) -> Narrative:
    logger.debug(f"Creating narrative block before next artifact.")
    lm = get_model().model

    # generate summary of story until now
    # summary = summarize(narrative_before)
    summary = narrative_before

    with system():
        lm += ("You are a game dialogue generator AI. Given a set of characters and a summary of what has happened in "
               "the story so far, your task is to continue the narrative with a sequence of one-line character "
               "interventions. Each intervention should be natural, engaging, and contribute to the progression of "
               "the story. Maintain coherence, respect character personalities, and ensure smooth dialogue flow. The "
               "conversation should naturally lead the player to the provided clue, integrating it seamlessly into "
               "the narrative.\n")
    with user():
        lm += (f"Continue the following story with a sequence of one-line character interventions. Use natural "
               f"dialogue that reflects the characters' personalities and moves the story forward. Ensure that the "
               f"conversation naturally leads the player to the provided clue.\n\n")
        lm += "Input:\n"
        lm += f"- This is a summary of the story until now: {summary}\n"
        lm += f"- You should focus on: {focus}\n"
        lm += f"- You should follow this style: {narrative_style}\n"
        lm += f"- The clue after this narrative will focus on: {clue_focus}\n"
        lm += f"- Use the following characters:\n"
        for i, character in enumerate(available_characters):
            lm += f"{character.name}: {character.description}\n"
        lm += f"- Use no more than {max_interactions} interactions.\n"
        lm += "- Keep interactions simple and easy to follow.\n"
        lm += "- Each interaction must be exactly a line long.\n"

    lm += create_dialogue_from_input(available_characters=available_characters, max_interactions=max_interactions)
    return create_narrative_stage_from_llm(lm)
