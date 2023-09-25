import os
import sys
import typing
import copy
import logging
from typing import Any, Optional, Text, Dict, List, Type
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

log_format = (
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s"
)
logging.basicConfig(filename="debug.log", level=logging.DEBUG, format=log_format)

debug_logger = logging.getLogger("debug")
error_logger = logging.getLogger("error")
info_logger = logging.getLogger("info")

debug_handler = logging.FileHandler("debug.log")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter(log_format))

info_handler = logging.FileHandler("info.log")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(log_format))

error_handler = logging.FileHandler("error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format))

debug_logger.addHandler(debug_handler)
info_logger.addHandler(info_handler)
error_logger.addHandler(error_handler)


if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(root_folder)

from riva.nlp.nlp import get_intent_and_entities


class RivaNLPComponent(Component):
    """Riva NLP component"""

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""
        return []

    defaults = {}

    supported_language_list = None
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component."""
        pass

    def __convert_to_rasa_intent(self, response):
        if not response["intent"]:
            error_logger.error("[Riva NLU] Intent is None in RivaNLPComponent class")
            return None
        intent_name = response["intent"]["value"].replace("_yes_no", "").replace("weather__temperature", "weather__temprature")
        intent = {"name": intent_name, "confidence": response["intent"]["confidence"]}
        return intent

    def __convert_to_rasa_entities(self, response):
        """Convert model output into the Rasa NLU compatible output format."""
        entities = []
        for entity in response["entities"]:
            entity["extractor"] = "RivaNLPExtractor"
            if entity["entity"] == "location":
                entity2 = copy.deepcopy(entity)
                entity2["entity"] = "city"
                entities.append(entity2)
            entities.append(entity)
        return entities


    def process(self, message: Message, **kwargs: Any) -> None:
        message_dict = message.as_dict()
        if 'text' in message_dict:
            response = get_intent_and_entities(message_dict['text'])
            info_logger.info("[Riva NLU] Riva Response: %s", response)
            intent = self.__convert_to_rasa_intent(response)
            if intent:
                message.set("intent", intent, add_to_output=True)
            entities = self.__convert_to_rasa_entities(response)
            message.set("entities", entities, add_to_output=True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""
        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""
        if cached_component:
            return cached_component
        else:
            return cls(meta)
