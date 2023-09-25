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
    This action is executed when verification is successful.
    It performs the following steps:
    1. Logs verification success.
    2. Responds with a verification success message.
    3. Deletes the lock for the conversation.
    4. Logs the deletion of the lock.
    5. Sends an end call message.
    6. Restarts the conversation.
    """

    def name(self) -> Text:
        return "action_agent_transfer"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        slot_failure_flag = tracker.get_slot("slot_failure_flag")
        conversation_id = tracker.sender_id
        inpu_channel = tracker.get_latest_input_channel()
        if  slot_failure_flag:
            # Log verification failed
            debug_logger.debug("Verification failed")

            info_logger.info(f"Action Verification Failed Tranfering call to live agent: {conversation_id}")

            # Get conversation text data
            conversation_text = "\n".join(
                [event["text"] for event in tracker.events if "text" in event]
            )
            # Calculate time taken
            time_taken = tracker.events[-1].get("timestamp") - tracker.events[0].get(
                "timestamp"
            )

            data = {
                "conversation_index": conversation_id,
                "conversation_text_data": conversation_text,
                "caller_verification_successful": "N",
                "time_taken": time_taken,
                "failure_field": "ssn",
            }
            Mongo_obj = MongoDataManager()
            Mongo_obj.save_data(data)
            conversation_id = tracker.sender_id

            self.get_handoff(inpu_channel, dispatcher, tracker, domain)

            # Respond with a verification end message
            dispatcher.utter_message(response="utter_verification_failed")
            
            # Delete the lock for the conversation
            InMemoryLockStore().delete_lock(conversation_id)

            # Log the deletion of the lock
            debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")

            # Send an end call message
            dispatcher.utter_message(response="utter_twilio_end_call")

            # Restart the conversation
            return [Restarted()]
            
        else:
            # Log verification success
            debug_logger.debug("Verification success")

            # Get conversation text data
            conversation_text = "\n".join(
                [event["text"] for event in tracker.events if "text" in event]
            )
            # Calculate time taken
            time_taken = tracker.events[-1].get("timestamp") - tracker.events[0].get(
                "timestamp"
            )

            data = {
                "conversation_index": conversation_id,
                "conversation_text_data": conversation_text,
                "caller_verification_successful": "Y",
                "time_taken": time_taken,
                "failure_field": None,
            }
            Mongo_obj = MongoDataManager()
            Mongo_obj.save_data(data)
            conversation_id = tracker.sender_id


            #Log the info that conversation successful
            info_logger.info(f"Action Verification succesfull Tranfering call to live agent: {conversation_id}")

            self.get_handoff(inpu_channel, dispatcher, tracker, domain)

            # Respond with a verification success message
            dispatcher.utter_message(response="utter_verification_success")

            # Delete the lock for the conversation
            InMemoryLockStore().delete_lock(conversation_id)

            # Log the deletion of the lock
            debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")

            # Send an end call message
            dispatcher.utter_message(response="utter_twilio_end_call")

            # Restart the conversation
            return [Restarted()]


    def get_handoff(self, inpu_channel, dispatcher, tracker, domain):
        if inpu_channel == "twilio_voice":
                handoff_obj = twillio_handoff()
                handoff_obj.run(dispatcher, tracker, domain)
        elif inpu_channel == "Voximplant_voice":
            handoff_obj = voximplant_handoff()
            handoff_obj.run(dispatcher, tracker, domain)
        else:
            handoff_obj = ActionBotToWebUITransfer()
            handoff_obj.run(dispatcher, tracker, domain)
        return None