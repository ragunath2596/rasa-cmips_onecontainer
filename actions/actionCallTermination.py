import logging
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, Action
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


from difflib import SequenceMatcher
from rasa.core.lock_store import InMemoryLockStore



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

class ActionChatTermination(Action):
    """
    Custom Rasa action to terminate a call.

    This action is executed when a conversation needs to be terminated.
    It deletes the lock associated with the conversation, sends a termination message,
    and triggers a conversation restart.
    """

    def name(self) -> Text:
        return "action_call_terminated"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        """
        Execute the termination action.

        Args:
            dispatcher (CollectingDispatcher): The Rasa dispatcher for sending messages.
            tracker (Tracker): The Rasa conversation tracker.
            domain (DomainDict): The Rasa domain configuration.

        Returns:
            List[Dict[Text, Any]]: List of Rasa events triggered by this action.
        """
        conversation_id = tracker.sender_id
        lock_store = InMemoryLockStore()  # Instantiate the lock_store
        lock_store.delete_lock(conversation_id)
        

        #Log the info that conversation successful
        info_logger.info(f"Action call termination: {conversation_id}")

        # Log the termination and lock deletion
        debug_logger.debug("Terminating call")
        debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")
        
        # Send termination message
        dispatcher.utter_message(response="utter_twilio_end_call")
        
        return [Restarted()]
