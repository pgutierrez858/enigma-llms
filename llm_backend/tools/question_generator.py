from guidance import system, user, assistant, gen
from loguru import logger

from llm_backend.llm_backend import get_model
from llm_backend.tools.regex_utils import sentence_regex, sentence_stop_regex, question_regex, question_stop_regex
from models.mc_question import McQuestion


def generate_mc_question(artifact_name: str,
                         artifact_description: str,
                         n_answers: int,
                         focus: str,
                         difficulty: str,
                         question_style: str) -> McQuestion:
    logger.debug("Generating MC Question")

    lm = get_model().model

    with system():
        lm += ("You are a multiple-choice question generator AI. Your task is to create multiple-choice questions "
               "based on a given text. Each question should have one correct answer and a specified number of "
               "plausible but incorrect distractors. Ensure that the questions are clear, relevant to the text, "
               "and appropriately challenging. The distractors should be logical and not easily dismissible.\n")
    with user():
        lm += (f"Generate a multiple-choice question based on the following text. The question should have one correct "
               f"answer and {n_answers-1} distractors. The question should be clear, relevant, and appropriately "
               "challenging, and be based solely on the information given in the text.\n\n")
        lm += "Input:\n"
        lm += f"- Artifact on which to generate question: {artifact_name}.\n"
        lm += f"- Text: {artifact_description}\n"
        lm += f"- Question should have difficulty: {difficulty}.\n"
        lm += f"- Question must be exactly a line long and follow this style: {question_style}.\n"
        lm += f"- Each answer must be exactly a line long.\n"
        lm += f"- Keep the focus on: {focus}.\n"

    with assistant():
        lm += "Question: " + gen(max_tokens=100, regex=question_regex, stop_regex=question_stop_regex,
                                 name='question', suffix='\n')
        logger.debug(f"Created question: [{lm['question']}]")
        lm += "Correct Answer: " + gen(max_tokens=100, regex=sentence_regex, stop_regex=sentence_stop_regex,
                                       name='correct_answer', suffix='\n')
        logger.debug(f"Created correct answer: [{lm['correct_answer']}]")
        for i in range(n_answers - 1):
            lm += (f"Distractor {i + 1}: " +
                   gen(max_tokens=100, regex=sentence_regex, stop_regex=sentence_stop_regex,
                       list_append=True, name='distractors', suffix='\n'))
            logger.debug(f"Created distractor {i + 1}: [{lm['distractors'][i]}]")
        question = McQuestion(
            artifact_name=artifact_name, question=lm['question'],
            correct_answer=lm['correct_answer'], distractors=lm['distractors'],
        )
    return question
