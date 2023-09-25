from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
from typing import Text, List, Dict, Any

class ActionBotToWebUITransfer(Action):
    def name(self) -> str:
        return 'action_bot_to_webui_transfer'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[EventType]:
        # Replace 'web_ui_url' with the actual URL or endpoint for the web UI
        web_ui_url = 'https://example.com/web_ui_transfer'

        # You can include any relevant information in the payload
        payload = {
            'message': 'Transfer to Web UI requested',
            'user_id': tracker.sender_id,
            'conversation_id': tracker.sender_id,  # Replace with a unique conversation identifier
        }

        # You should implement the logic to send the payload to the web UI here
        # You can use libraries like requests to make HTTP POST requests to the web UI endpoint

        # Example using requests library
        # import requests
        # response = requests.post(web_ui_url, json=payload)

        dispatcher.utter_message("Transferring to Web UI.")

        return []
