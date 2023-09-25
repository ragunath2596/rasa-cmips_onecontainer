import logging
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.rest import Client
from typing import List, Dict, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType

from twilio.twiml.voice_response import Dial, VoiceResponse
from twilio.rest import Client
from typing import List, Dict, Any, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType


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
        return 'action_transfer_to_twilio_agent'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        user_info = self.get_user_info(tracker)
        debug_logger.debug(f"transfer call to twillio")
        debug_logger.debug(f"user_info : {user_info}")


        return []

    def get_user_info(self, tracker: Tracker) -> Dict[str, Any]:
        return {
            "user_type": tracker.get_slot("user_type") or "provider",
            "provider_number": tracker.get_slot("slot_provider_number"),
            "name": tracker.get_slot("slot_provider_name"),
            "ssn": tracker.get_slot("slot_provider_ssn"),
            "county": tracker.get_slot("slot_provider_county"),
        }

    def get_handoff_bot_config(self, handoff_to: str) -> Dict[str, Any]:
        # You should implement this method to retrieve the configuration.
        # Example: handoff_config.get(handoff_to, {})
        return {}

    def get_twilio_client(self) -> Client:
        # Initialize and return the Twilio client here.
        # return Client(account_sid, auth_token)
        pass

    def create_twiml_response(self) -> VoiceResponse:
        return VoiceResponse()

    def dial_to_agent(self, twiml_response: VoiceResponse, client: Client):
        dial = Dial()
        # dial.number(agent_phone_number)
        twiml_response.append(dial)

    def handle_handoff_response(
        self, dispatcher: CollectingDispatcher, url: str, tracker: Tracker
    ):
        if url:
            if tracker.get_latest_input_channel() == "rest":
                dispatcher.utter_message(
                    json_message={
                        "handoff_host": url,
                        "title": "Helpdesk Assistant",
                    }
                )
            else:
                dispatcher.utter_message(
                    template="utter_wouldve_handed_off",
                    handoffhost=url
                )
        else:
            dispatcher.utter_message(template="utter_no_handoff")

