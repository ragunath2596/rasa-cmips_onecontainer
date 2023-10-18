import logging
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, Action
from rasa.core.lock_store import InMemoryLockStore
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import Restarted
from database import mongo
from database.mongo import MongoDataManager


lock_store = InMemoryLockStore()
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


class ActionVerificationFailed(Action):
    """
    This action is executed when verification fails.
    It performs the following steps:
    1. Logs verification failure.
    2. Responds with a verification failed message.
    3. Deletes the lock for the conversation.
    4. Logs the deletion of the lock.
    5. Sends an end call message.
    6. Restarts the conversation.
    """

    def name(self) -> Text:
        return "action_verification_failed"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Log verification failure
        debug_logger.debug("Verification failed")

        # Respond with a verification failed message
        dispatcher.utter_message(response="utter_verification_failed")

        # Delete the lock for the conversation
        conversation_id = tracker.sender_id
        lock_store.delete_lock(conversation_id)

        # Log the deletion of the lock
        debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")

        # Send an end call message
        dispatcher.utter_message(response="utter_twilio_end_call")

        # Restart the conversation
        return [Restarted()]
