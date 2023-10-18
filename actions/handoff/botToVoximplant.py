import logging
from typing import List, Dict, Any, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
from rasa.core.lock_store import InMemoryLockStore
from rasa_sdk.events import Restarted

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



class ActionHandoff(Action):
    def name(self) -> str:
        return 'action_transfer_to_voximplant_agent'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        user_info = self.get_user_info(tracker)
        dispatcher.utter_message(template="utter_handoff")
        debug_logger.debug(f"transfer call to VOXIMPLANT")
        debug_logger.debug(f"user_info : {user_info}")

        conversation_id = tracker.sender_id

        InMemoryLockStore().delete_lock(conversation_id)

        # Log the deletion of the lock
        debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")

        # Send an end call message
        dispatcher.utter_message(response="utter_twilio_end_call")

        # Restart the conversation
        return [Restarted()]


    def get_user_info(self, tracker: Tracker) -> Dict[str, Any]:
        return {
            "user_type": tracker.get_slot("slot_user_type"),
            "provider_number": tracker.get_slot("slot_provider_number"),
            "name": tracker.get_slot("slot_provider_name"),
            "ssn": tracker.get_slot("slot_provider_ssn"),
            "county": tracker.get_slot("slot_provider_county"),
        }

    def get_handoff_bot_config(self, handoff_to: str) -> Dict[str, Any]:
        # You should implement this method to retrieve the configuration.
        # Example: handoff_config.get(handoff_to, {})
        return {}

    # def create_voximplant_session(self, vox_api: VoximplantAPI) -> str:
    #     # Create a Voximplant session, you can choose either voice or chat
    #     voice_api = VoiceAPI(api=vox_api)
    #     session_id = voice_api.create_call(
    #         rule_id='YOUR_RULE_ID', # Specify a Voximplant rule for routing
    #         from_=user_info['user_type'],
    #         to='AGENT_PHONE_NUMBER',
    #         caller_id=user_info['name'],
    #     )
    #     return session_id

    def handle_handoff_response(
        self, dispatcher: CollectingDispatcher, session_id: str
    ):
        if session_id:
            dispatcher.utter_message(
                text=f"You are being connected to an agent. Your session ID is: {session_id}"
            )
        else:
            dispatcher.utter_message(template="utter_no_handoff")
