import logging
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, Action
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher

# Configure logging with a custom log formatter

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


# Helper function to log messages
def log_message(message):
    """Log a message to the configured logging system."""
    logging.debug(message)


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Execute the fallback action.

        Args:
            dispatcher (CollectingDispatcher): Rasa dispatcher to send messages.
            tracker (Tracker): The current conversation tracker.
            domain (Dict[Text, Any]): The domain configuration.

        Returns:
            List[Dict[Text, Any]]: A list of events to be processed.
        """
        user_input = tracker.latest_message["text"]

        # Log the user input
        info_logger.info(f"IVR input FB: {user_input}")

        # Respond with a fallback message
        dispatcher.utter_message(response="utter_fallback")

        # Revert the last user utterance to return to the previous state
        return [UserUtteranceReverted()]
