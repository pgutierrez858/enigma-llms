from guidance import models
from loguru import logger

from models.adventure import Adventure


class LLMBackend:
    def __init__(self, base_model):
        self.adventure = Adventure(characters=[], artifacts=[], stages=[])
        self.model = base_model
        self.original_model = self.model.copy()

    def reset(self):
        self.adventure = Adventure(characters=[], artifacts=[], stages=[])
        self.model = self.original_model


llm_backend: LLMBackend | None = None


def reset_model():
    global llm_backend
    if llm_backend is not None:
        llm_backend.reset()


def get_model() -> LLMBackend:
    global llm_backend
    if llm_backend is None:
        logger.debug("Initializing LLM Backend")
        logger.debug("Loading language model")
        llama3 = models.LlamaCpp(model="C:/Users/Pablo/AppData/Local/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0"
                                       ".gguf", n_ctx=8192,
                                 seed=-1,
                                 n_gpu_layers=-1)
        llm_backend = LLMBackend(llama3)
    return llm_backend
