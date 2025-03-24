from loguru import logger

from data.artifact_dataset import get_all
from experiments.config import ConfigModel
from experiments.times import clear_timer
from llm_backend.llm_backend import get_model, reset_model
from llm_backend.planned_adventure_generator import create_planned_adventure_from_user_input
from llm_backend.raw_adventure_generator import create_adventure_from_raw_input
from models.artifact_data import ArtifactData


# Add a new artifact
def add_artifact(name, description):
    adventure = get_model().adventure
    artifact = ArtifactData(name=name, description=description, facts=[])
    if adventure.try_add_artifact(artifact):
        logger.debug(f"Artifact '{name}' added successfully.")
    else:
        logger.debug(f"Artifact '{name}' could not be added.")


def fetch_artifact_from_knowledge_base(artifact_name):
    adventure = get_model().adventure
    if not adventure.artifacts or len(adventure.artifacts) == 0:
        logger.debug("No artifacts available.")
        return None

    artifact = next((x for x in adventure.artifacts if x.name == artifact_name), None)
    if artifact is None:
        logger.debug(f"Artifact '{artifact_name}' could not be found in knowledge base")
        return None
    return artifact


def run_experiment(config: ConfigModel, preprocess=True):
    reset_model()
    clear_timer()

    for artifact in get_all():
        add_artifact(artifact['name'], artifact['description'])

    adventure = get_model().adventure

    if preprocess:
        create_planned_adventure_from_user_input(config)
    else:
        create_adventure_from_raw_input(config)

    return adventure
