import logging
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, Action
from rasa.core.lock_store import InMemoryLockStore
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import Restarted
from database import mongo
from database.mongo import MongoDataManager
from actions.handoff.botToIVRTwillio import ActionHandoff as twillio_handoff
from actions.handoff.botToVoximplant import ActionHandoff as voximplant_handoff
from actions.handoff.botToWebapp import ActionBotToWebUITransfer




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

class ActionAgentTransfer(Action):
    """
    Action for handling the transfer of a conversation to a live agent based on verification success or failure.

    This action performs the following steps:
    1. Logs verification success or failure.
    2. Saves conversation data to MongoDB.
    3. Initiates a handoff based on the input channel.
    4. Responds with a verification success or failure message.
    5. Deletes the lock for the conversation.
    6. Sends an end call message.
    7. Restarts the conversation.
    """

    def name(self) -> Text:
        """
        Returns the name of the action.
        """
        return "action_agent_transfer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        """
        Executes the action.

        Args:
            dispatcher (CollectingDispatcher): Dispatcher to send messages.
            tracker (Tracker): Conversation tracker.
            domain (DomainDict): Domain configuration.

        Returns:
            List[Dict[Text, Any]]: List of events to be processed.
        """
        slot_failure_flag = tracker.get_slot("slot_failure_flag")
        conversation_id = tracker.sender_id
        input_channel = tracker.get_latest_input_channel()

        # Log verification success or failure
        log_verification(slot_failure_flag, conversation_id, tracker)

        # Get conversation text data
        conversation_text = "\n".join([event["text"] for event in tracker.events if "text" in event])

        # Calculate time taken
        time_taken = tracker.events[-1]["timestamp"] - tracker.events[0]["timestamp"]

        # Save data to MongoDB
        save_data_to_mongo(conversation_id, conversation_text, slot_failure_flag, time_taken)

        # Perform handoff based on input channel
        self.get_handoff(input_channel, dispatcher, tracker, domain)

        # Respond with verification message
        response_message = "utter_verification_failed" if slot_failure_flag else "utter_verification_success"
        dispatcher.utter_message(response=response_message)

        # Delete the lock for the conversation
        InMemoryLockStore().delete_lock(conversation_id)
        debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")

        # Restart the conversation
        return [Restarted()]

    def get_handoff(self, input_channel, dispatcher, tracker, domain):
        """
        Initiates the handoff based on the input channel.

        Args:
            input_channel (str): Input channel for the conversation.
            dispatcher (CollectingDispatcher): Dispatcher to send messages.
            tracker (Tracker): Conversation tracker.
            domain (DomainDict): Domain configuration.
        """
        handoff_obj = (
            twillio_handoff() if input_channel == "twilio_voice"
            else voximplant_handoff() if input_channel == "Voximplant_voice"
            else ActionBotToWebUITransfer()
        )
        handoff_obj.run(dispatcher, tracker, domain)
        return True

def log_verification(slot_failure_flag, conversation_id, tracker):
    """
    Logs the verification success or failure.

    Args:
        slot_failure_flag (bool): Flag indicating verification failure.
        conversation_id (str): ID of the conversation.
        tracker (Tracker): Conversation tracker.
    """
    debug_logger.debug("Verification failed" if slot_failure_flag else "Verification success")
    info_logger.info(f"Action Verification {'failed' if slot_failure_flag else 'successful'} "
                     f"Transferring call to live agent: {conversation_id}")
    return True

def save_data_to_mongo(conversation_id, conversation_text, slot_failure_flag, time_taken):
    """
    Saves conversation data to MongoDB.

    Args:
        conversation_id (str): ID of the conversation.
        conversation_text (str): Text data of the conversation.
        slot_failure_flag (bool): Flag indicating verification failure.
        time_taken (float): Time taken for the conversation.
    """
    data = {
        "conversation_index": conversation_id,
        "conversation_text_data": conversation_text,
        "caller_verification_successful": "N" if slot_failure_flag else "Y",
        "time_taken": time_taken,
        "failure_field": "ssn" if slot_failure_flag else None,
    }
    MongoDataManager().save_data(data)
    return True
