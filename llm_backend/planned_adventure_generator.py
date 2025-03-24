from guidance import system, user, assistant, gen
from loguru import logger

from experiments.config import ConfigModel
from experiments.times import timer
from llm_backend.llm_backend import get_model
from llm_backend.tools.character_generator import generate_adventure_characters
from llm_backend.tools.clue_generator import generate_clue_to_artifact
from llm_backend.tools.dialogue_generators import create_introduction_narrative, create_narrative_block_before_artifact, \
    create_ending_narrative
from llm_backend.tools.fact_extractor import extract_facts
from llm_backend.tools.question_generator import generate_mc_question
from llm_backend.tools.regex_utils import sentence_regex, sentence_stop_regex
from models.adventure_plan import AdventurePlan
from models.clue import CluePlan
from models.mc_question import McQuestionPlan
from models.narrative import NarrativePlan


def create_planned_adventure_from_user_input(user_input: ConfigModel):
    adventure = get_model().adventure

    with timer('fact_extraction'):
        for artifact in adventure.artifacts:
            artifact.facts = extract_facts(artifact_name=artifact.name,
                                           artifact_description=artifact.description,
                                           number_of_facts=1,
                                           focus=user_input.focus)

    adventure_plan = AdventurePlan(artifacts_to_find=adventure.artifacts,
                                   narrative_style=user_input.narrative_style,
                                   clue_style=user_input.fact_style,
                                   question_style=user_input.question_style,
                                   max_narrative_length=user_input.max_narrative_length,
                                   answers_per_question=user_input.answers_per_question,
                                   target_audience=user_input.target_audience,
                                   difficulty=user_input.difficulty,
                                   intention=user_input.intention,
                                   general_description=user_input.general_description)
    with timer('plan_generation'):
        generate_questions_and_clues_plan(adventure_plan)
        generate_narrative_plan(adventure_plan)
        adventure.characters = adventure_plan.characters

    story_until_now = []
    for artifact in adventure.artifacts:
        artifact.facts = [artifact.description]

    with timer('narrative_start'):
        narrative = create_introduction_narrative(available_characters=adventure.characters,
                                                  max_interactions=user_input.max_narrative_length,
                                                  narrative_style=user_input.narrative_style,
                                                  focus=adventure_plan.planned_intro.focus)
        adventure.try_add_stage_at_position(narrative, len(adventure.stages))
        story_until_now += [f"{d.character_name}: {d.intervention_text}" for d in narrative.interventions]

    # artifact sequences
    for i, artifact in enumerate(adventure.artifacts):
        pre_story = "\n".join(story_until_now)

        with timer(f'clue_{i}'):
            clue = generate_clue_to_artifact(artifact_name=artifact.name,
                                             artifact_description=artifact.facts[0],
                                             clue_style=user_input.clue_style,
                                             difficulty=user_input.difficulty,
                                             focus=adventure_plan.planned_clues[i].focus)

        with timer(f'narrative_{i}'):
            narrative = create_narrative_block_before_artifact(available_characters=adventure.characters,
                                                               narrative_before=pre_story,
                                                               max_interactions=user_input.max_narrative_length,
                                                               narrative_style=user_input.narrative_style,
                                                               focus=adventure_plan.planned_narratives[i].focus,
                                                               clue_focus=clue.text)
            story_until_now += [f"{d.character_name}: {d.intervention_text}" for d in narrative.interventions]

        with timer(f'question_{i}'):
            question = generate_mc_question(artifact_name=artifact.name,
                                            artifact_description=artifact.description,
                                            n_answers=user_input.answers_per_question,
                                            question_style=user_input.question_style,
                                            difficulty=user_input.difficulty,
                                            focus=adventure_plan.planned_questions[i].focus)

        # add narrative before clue
        adventure.try_add_stage_at_position(narrative, len(adventure.stages))
        adventure.try_add_stage_at_position(clue, len(adventure.stages))
        adventure.try_add_stage_at_position(question, len(adventure.stages))

    # ending
    pre_story = "\n".join(story_until_now)
    with timer('narrative_end'):
        narrative = create_ending_narrative(available_characters=adventure.characters,
                                            narrative_before=pre_story,
                                            max_interactions=user_input.max_narrative_length,
                                            narrative_style=user_input.narrative_style,
                                            focus=adventure_plan.planned_outro.focus)
        adventure.try_add_stage_at_position(narrative, len(adventure.stages))


def generate_questions_and_clues_plan(adventure_plan: AdventurePlan):
    lm = get_model().model

    with system():
        lm += ("You are a treasure hunt planner AI. Your task is to suggest ideas for treasure hunt clues based on a "
               "set of artifact descriptions. These clues should be cohesive and connect logically, guiding players "
               "toward the artifacts without directly naming them. Additionally, suggest thematic test questions that "
               "players can answer to demonstrate their knowledge of each artifact. Ensure the clues and questions "
               "follow a common linking pattern to maintain cohesion throughout the adventure. Your suggestions "
               "should create an engaging and immersive experience that ties the artifacts and challenges together in "
               "a meaningful way.\n")

    with user():
        # Introduce the game planning context
        lm += ("Given the following set of artifact descriptions, suggest ideas for treasure hunt clues and thematic "
               "test questions. The clues should guide players to each artifact while maintaining a cohesive linking "
               "pattern. The test questions should help players demonstrate their knowledge of each artifact, "
               "based on its unique characteristics and historical context. Ensure the clues and questions follow a "
               "common theme to tie the adventure together.\n\n")

        lm += "Input:\n"

        # Define game constraints
        lm += f"- Try to match this design intention: {adventure_plan.intention}.\n"
        lm += f"- Game should be engaging to the target audience: {adventure_plan.target_audience}.\n"
        lm += f"- Game should have difficulty:{adventure_plan.difficulty}.\n"
        lm += f"- Game should fit this overall description: {adventure_plan.general_description}.\n"
        lm += f"- Both question and clue ideas must be exactly one line long.\n"
        lm += f"- Questions have style: {adventure_plan.question_style}.\n"
        lm += f"- Clues have style: {adventure_plan.clue_style}.\n"

    # List the artifacts with key facts
    for idx, artifact in enumerate(adventure_plan.artifacts_to_find):
        with user():
            lm += f"- Artifact {idx + 1}: {artifact.name}\n"
            for j, fact in enumerate(artifact.facts):
                lm += f"  - Description {j + 1}: {fact}\n"

        with assistant():
            lm += f"The clue for '{artifact.name}' should focus on "
            lm += gen(max_tokens=150,
                      regex=sentence_regex,
                      stop_regex=sentence_stop_regex,
                      list_append=True,
                      name="clue_focus")
            logger.debug(f"Clue Focus for {artifact.name}: [{lm['clue_focus'][-1]}]")
            clue_plan = CluePlan(artifact_name=artifact.name,
                                 facts_to_consider=artifact.facts,
                                 difficulty=adventure_plan.difficulty,
                                 clue_style=adventure_plan.clue_style,
                                 focus=lm['clue_focus'][idx])
            adventure_plan.planned_clues.append(clue_plan)

            lm += f"The question about '{artifact.name}' should test player on "
            lm += gen(max_tokens=150,
                      regex=sentence_regex,
                      stop_regex=sentence_stop_regex,
                      list_append=True,
                      name="question_focus")
            logger.debug(f"Question Focus for {artifact.name}: [{lm['question_focus'][-1]}]")
            question_plan = McQuestionPlan(artifact_name=artifact.name,
                                           facts_to_consider=artifact.facts,
                                           difficulty=adventure_plan.difficulty,
                                           question_style=adventure_plan.question_style,
                                           focus=lm['question_focus'][idx],
                                           n_answers=adventure_plan.answers_per_question)
            adventure_plan.planned_questions.append(question_plan)


def generate_narrative_plan(adventure_plan: AdventurePlan):
    lm = get_model().model

    with system():
        lm += ("You are a treasure hunt narrative planner AI. Your task is to create a structured narrative plan based "
               "on a set of artifact descriptions and their corresponding clues. This plan should outline the key "
               "story elements—such as the progression of the hunt and settings—without writing "
               "the actual narrative. The plan should detail how each clue and artifact will lead the player through "
               "the adventure, and how characters and plot points will tie into the overall journey. Ensure that the "
               "structure maintains a cohesive flow, with each clue leading logically to the next stage of the hunt.\n")

    with user():
        lm += ("Based on the following artifact descriptions and clues, generate a structured narrative plan for a "
               "treasure hunt. The plan should outline key plot points, the sequence of clues, "
               "and settings involved, ensuring a logical and cohesive adventure. This is a high-level outline, "
               "not the full narrative.\n")

        lm += "Input:\n"
        # Define game constraints
        lm += f"- Try to match this design intention: {adventure_plan.intention}.\n"
        lm += f"- Game should be engaging to the target audience: {adventure_plan.target_audience}.\n"
        lm += f"- Game should fit this overall description: {adventure_plan.general_description}.\n"
        lm += f"- Game should follow this narrative style: {adventure_plan.narrative_style}.\n"

        # generate characters
        with timer('character_generation'):
            lm += "You may only use the following characters:\n"
            adventure_plan.characters = generate_adventure_characters(n_characters=2,
                                                                      general_overview=adventure_plan.general_description,
                                                                      target_audience=adventure_plan.target_audience,
                                                                      intention=adventure_plan.intention,
                                                                      narrative_style=adventure_plan.narrative_style)
            for character in adventure_plan.characters:
                lm += f"{character.name}: {character.description}.\n"

    with user():
        lm += "Start by providing a single sentence outline for the introduction of the game.\n"
    with assistant():
        # Generate Introduction Narrative Plan
        lm += "Introduction Narrative Focus (single sentence): "
        lm += gen(max_tokens=250,
                  regex=sentence_regex,
                  stop_regex=sentence_stop_regex,
                  name="introduction_narrative")
        logger.debug(f"Introduction Narrative Plan: [{lm['introduction_narrative']}]")
        narrative_plan = NarrativePlan(artifact_name="Start of the Game",
                                       characters_available=adventure_plan.characters,
                                       narrative_style=adventure_plan.narrative_style,
                                       max_interactions=adventure_plan.max_narrative_length,
                                       focus=lm['introduction_narrative'])
        adventure_plan.planned_intro = narrative_plan

    for idx, artifact in enumerate(adventure_plan.artifacts_to_find):
        with user():
            lm += (f"Now provide a single sentence outline of the narrative before the player having to look for the"
                   f"following artifact:\n")
            lm += f"- Artifact {idx + 1}: {artifact.name}\n"
            for j, fact in enumerate(artifact.facts):
                lm += f"  - Description {j + 1}: {fact}\n"
            lm += f"- Clue idea: {adventure_plan.planned_clues[idx].focus}.\n"
        with assistant():
            lm += f"Narrative Focus for this block (single sentence): "
            lm += gen(max_tokens=250,
                      regex=sentence_regex,
                      stop_regex=sentence_stop_regex,
                      name="narrative_plan",
                      list_append=True)
            logger.debug(f"Narrative Focus for {artifact.name}: [{lm['narrative_plan'][-1]}]")
            narrative_plan = NarrativePlan(artifact_name="Start of the Game",
                                           characters_available=adventure_plan.characters,
                                           narrative_style=adventure_plan.narrative_style,
                                           max_interactions=adventure_plan.max_narrative_length,
                                           focus=lm['narrative_plan'][-1])
            adventure_plan.planned_narratives.append(narrative_plan)

    with user():
        lm += "Now provide a single sentence outline for the ending of the game.\n"
    with assistant():
        lm += "Final Narrative Focus (single sentence): "
        lm += gen(
            max_tokens=250,
            regex=sentence_regex,
            stop_regex=sentence_stop_regex,
            name="final_narrative")
        logger.debug(f"Final Narrative Plan: [{lm['final_narrative']}]")
        narrative_plan = NarrativePlan(artifact_name="Start of the Game",
                                       characters_available=adventure_plan.characters,
                                       narrative_style=adventure_plan.narrative_style,
                                       max_interactions=adventure_plan.max_narrative_length,
                                       focus=lm['final_narrative'])
        adventure_plan.planned_outro = narrative_plan
