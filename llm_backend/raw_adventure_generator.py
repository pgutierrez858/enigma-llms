from experiments.config import ConfigModel
from experiments.times import timer
from llm_backend.llm_backend import get_model
from llm_backend.tools.character_generator import generate_adventure_characters
from llm_backend.tools.clue_generator import generate_clue_to_artifact
from llm_backend.tools.dialogue_generators import create_introduction_narrative, create_narrative_block_before_artifact, \
    create_ending_narrative
from llm_backend.tools.question_generator import generate_mc_question


def create_adventure_from_raw_input(user_input: ConfigModel):
    adventure = get_model().adventure

    # generate characters
    with timer('character_generation'):
        adventure.characters = generate_adventure_characters(n_characters=2,
                                                             general_overview=user_input.general_description,
                                                             narrative_style=user_input.narrative_style,
                                                             intention=user_input.intention,
                                                             target_audience=user_input.target_audience)

    story_until_now = []
    for artifact in adventure.artifacts:
        artifact.facts = [artifact.description]

    with timer('narrative_start'):
        narrative = create_introduction_narrative(available_characters=adventure.characters,
                                                  max_interactions=user_input.max_narrative_length,
                                                  narrative_style=user_input.narrative_style,
                                                  focus=user_input.general_description)
        adventure.try_add_stage_at_position(narrative, len(adventure.stages))
        story_until_now += [f"{d.character_name}: {d.intervention_text}" for d in narrative.interventions]

    # artifact sequences
    for i, artifact in enumerate(adventure.artifacts):
        pre_story = "\n".join(story_until_now)

        with timer(f'clue_{i}'):
            clue = generate_clue_to_artifact(artifact_name=artifact.name,
                                             artifact_description=artifact.description,
                                             clue_style=user_input.clue_style,
                                             difficulty=user_input.difficulty,
                                             focus='Highlight an aspect of the artifact in a clue for the player.')

        with timer(f'narrative_{i}'):
            narrative = create_narrative_block_before_artifact(available_characters=adventure.characters,
                                                               narrative_before=pre_story,
                                                               max_interactions=user_input.max_narrative_length,
                                                               narrative_style=user_input.narrative_style,
                                                               focus=f'Story events before giving next clue to the '
                                                                     f'player: {clue.text}.',
                                                               clue_focus=clue.text)
            story_until_now += [f"{d.character_name}: {d.intervention_text}" for d in narrative.interventions]

        with timer(f'question_{i}'):
            question = generate_mc_question(artifact_name=artifact.name,
                                            artifact_description=artifact.description,
                                            n_answers=user_input.answers_per_question,
                                            question_style=user_input.question_style,
                                            difficulty=user_input.difficulty,
                                            focus="Test player on a part of the artifact's history/meaning.")

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
                                            focus="Wrap up the ending and conclude the story.")
        adventure.try_add_stage_at_position(narrative, len(adventure.stages))
