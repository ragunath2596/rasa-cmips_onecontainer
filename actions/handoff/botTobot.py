from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher

import ruamel.yaml
import pathlib
from typing import Dict, Text, Any, List
from rasa_sdk.events import EventType

here = pathlib.Path(__file__).parent.absolute()
handoff_config = (
    ruamel.yaml.safe_load(open(f"{here}/handoff_config.yml", "r")) or {}
).get("handoff_hosts", {})


from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from typing import Text, List, Dict, Any

class ActionBotToBotTransfer(Action):
    def name(self) -> str:
        return 'action_bot_to_bot_transfer'

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[EventType]:
        # Assuming you have a slot that stores the target bot's name
        target_bot = tracker.get_slot("target_bot")

        if target_bot:
            # You can implement logic to determine how to transfer the conversation
            # to the target bot here. This could involve making API calls or other
            # communication methods.
            
            # For demonstration purposes, we'll set a slot to indicate the transfer.
            return [SlotSet("bot_transfer_successful", True)]
        else:
            dispatcher.utter_message("I'm sorry, I couldn't determine the target bot.")
            return []

# In your domain.yml, define an intent to trigger the bot-to-bot transfer:
# intents:
#   - bot_transfer_intent

# Create a story in your stories.md to trigger the transfer:
# ## Transfer to Another Bot
# * bot_transfer_intent
#   - action_bot_to_bot_transfer
