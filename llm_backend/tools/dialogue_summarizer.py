from guidance import system, user, assistant, gen
from loguru import logger

from llm_backend.llm_backend import get_model
from llm_backend.tools.regex_utils import text_regex, text_stop_regex


def summarize(text: str) -> str:
    logger.debug("Summarizing narrative until now.")

    lm = get_model().model
    with system():
        lm += ("You are a summarizer AI. Your task is to take in a sequence of dialogues and generate a short, "
               "simple summary of what happened in the conversation. Focus on key events, actions, or decisions made, "
               "and avoid unnecessary details. Keep the summary clear, concise, and to the point.\n")
    with user():
        lm += ("Please summarize the following dialogue in a short and simple way, focusing on key events, actions, "
               "or decisions made. Keep the summary concise and to the point.\n")
        lm += f"Dialogues:\n{text}\n"
    with assistant():
        lm += "Short summary: " + gen(max_tokens=200,
                                      regex=text_regex,
                                      stop_regex=text_stop_regex,
                                      name='summary')
        logger.debug(f"Summary until now: {lm['summary']}.")
    return lm['summary']
