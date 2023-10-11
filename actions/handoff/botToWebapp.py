import logging
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
from typing import Text, List, Dict, Any
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




class ActionBotToWebUITransfer(Action):
    def name(self) -> str:
        return 'action_bot_to_webui_transfer'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[EventType]:
        conversation_id = tracker.sender_id
        # Replace 'web_ui_url' with the actual URL or endpoint for the web UI
        web_ui_url = 'https://example.com/web_ui_transfer'

        # You can include any relevant information in the payload
        payload = {
            'message': 'Transfer to Web UI requested',
            'user_id': tracker.sender_id,
            'conversation_id': conversation_id,  # Replace with a unique conversation identifier
        }

        # You should implement the logic to send the payload to the web UI here
        # You can use libraries like requests to make HTTP POST requests to the web UI endpoint

        # Example using requests library
        # import requests
        # response = requests.post(web_ui_url, json=payload)
        user_info = self.get_user_info(tracker)

        debug_logger.debug(f"user_info : {user_info}")

        dispatcher.utter_message("Transferring to Web UI.")

        InMemoryLockStore().delete_lock(conversation_id)

        # Log the deletion of the lock
        debug_logger.debug(f"Deleted lock for conversation_id: {conversation_id}")

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
