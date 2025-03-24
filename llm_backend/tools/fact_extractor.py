from typing import List

from guidance import system, user, assistant, gen
from loguru import logger

from llm_backend.llm_backend import get_model
from llm_backend.tools.regex_utils import sentence_regex, sentence_stop_regex


def extract_facts(artifact_name: str,
                  artifact_description: str,
                  number_of_facts: int,
                  focus: str = 'coverage of source description') -> List[str]:
    logger.debug("Extracting artifact facts")

    lm = get_model().model

    with system():
        lm += ("You are a fact distillation AI. Your task is to extract the most relevant and interesting facts from a "
               "given text and present them as concise, engaging one-liners. Focus on key details that are "
               "insightful, surprising, or valuable. Ensure clarity, avoid redundancy, and make each fact stand alone "
               "as a compelling piece of information.\n")
    with user():
        lm += ("Extract the most relevant and interesting facts from the following text and present them as concise, "
               "engaging one-liners. Focus on key details that are insightful or surprising.\n\n")
        lm += "Input:\n"
        lm += f"- Artifact: {artifact_name}.\n"
        lm += f"- Text: {artifact_description}\n"
        lm += f"- Extract exactly {number_of_facts} facts from this text.\n"
        lm += f"- Each fact must be exactly a line long.\n"
        lm += f"- Keep the focus on: {focus}\n"

    with assistant():
        for i in range(number_of_facts):
            lm += f'Fact {i + 1}: ' + gen(max_tokens=100,
                                          regex=sentence_regex,
                                          stop_regex=sentence_stop_regex,
                                          list_append=True,
                                          name='facts',
                                          suffix='"\n')
            fact = lm['facts'][i]
            logger.debug(f"Created fact {i + 1}: [{fact}]")
    return lm['facts']
