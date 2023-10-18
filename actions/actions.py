import logging
import re
from difflib import SequenceMatcher
from typing import Text, List, Any, Dict

from nltk.stem import WordNetLemmatizer
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.types import DomainDict
from rasa_sdk.events import Restarted , SlotSet
from rasa_sdk.events import FollowupAction



from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from database.sqlite import (
    fetch_records_by_provider_number,
)  # Import your function here
import re
import logging
from typing import Text, Any, Dict

from database.mongo import MongoDataManager


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


def save_database_mongo(tracker, field_name, caller_verification):
    conversation_index = tracker.sender_id

    # Get conversation text data
    conversation_text = "\n".join(
        [event["text"] for event in tracker.events if "text" in event]
    )

    # Calculate time taken
    time_taken = tracker.latest_message["timestamp"] - tracker.events[0].get(
        "timestamp"
    )
    data = {
        "conversation_index": conversation_index,
        "conversation_text_data": conversation_text,
        "caller_verification_successful": caller_verification,
        "time_taken": time_taken,
        "failure_field": field_name,
    }

    Mongo_obj = MongoDataManager()
    Mongo_obj.save_data(data)


class ValidateCallerVerificationForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_caller_validation_form"
    
    async def validate_slot_user_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if (tracker.latest_message)['text'] == "call_terminated":
            return { "requested_slot": None}
        return {"slot_user_type": slot_value}

    async def validate_slot_provider_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_provider_number_failure_count = tracker.get_slot("slot_provider_number_failure_count") or 0

        number_ = re.sub(r"\D", "", str(tracker.latest_message["text"]))
        logging.debug(f"IVR input PNUM: {tracker.latest_message['text']}")
        logging.debug(f"Provider number slot value: {(slot_value)}")
        logging.debug(f"Pre-processed number: {number_}")

        # Fetch records using the function
        self.matching_records = fetch_records_by_provider_number(str(slot_value))

        # Compare fetched records with user input
        if self.matching_records:
            return {
                "slot_provider_number": slot_value,
                "slot_provider_number_failure_count": 0,
            }
        else:
            if slot_provider_number_failure_count >= 2:
                logging.debug(f"Provider number verification failed")

                dispatcher.utter_message(
                    response="utter_invalid_provider_number"
                )
                return {
                    "slot_provider_number": None,
                    "slot_provider_number_failure_count": 0,
                    "requested_slot": None,
                }
            else:
                logging.debug(f"Provider number verification failed")
                dispatcher.utter_message(
                    response="utter_invalid_provider_number"
                )
                save_database_mongo(tracker, "provider_number", "N")
                return {
                    "slot_provider_number": None,
                    "slot_provider_number_failure_count": slot_provider_number_failure_count + 1,
                }

    async def validate_slot_provider_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `slot_provider_name` value."""

        slot_provider_number_failure_count = tracker.get_slot("slot_provider_number_failure_count") or 0

        name_ = re.sub(r"\D", "", str(tracker.latest_message["text"]))
        logging.debug("Inside validate_provider_name")
        logging.debug(f"IVR input PNAME: {(tracker.latest_message)['text']}")

        # Retrieve matching records from the stored attribute
        matching_records = self.matching_records

        # Compare fetched records with user input
        try:
            if matching_records and matching_records[0]["full_name"] == str(slot_value):
                # Proceed with validation
                return {
                    "slot_provider_name": slot_value,
                    "slot_provider_number_failure_count": 0,
                }
            if slot_provider_number_failure_count >= 2:
                logging.debug(f"provider_name verification failed")

                dispatcher.utter_message(
                    response="utter_invalid_full_name"
                )
                return {
                    "slot_provider_name": None,
                    "slot_provider_number_failure_count": 0,
                    "requested_slot": None,
                }
            else:
                logging.debug(f"provider_name verification failed")
                dispatcher.utter_message(
                    response="utter_invalid_full_name"
                )
                save_database_mongo(tracker, "provider_name", "N")
                return {
                    "slot_provider_name": None,
                    "slot_provider_number_failure_count": slot_provider_number_failure_count + 1,
                }
        except Exception as e:
            logging.debug(
                f"index out of range error: {(tracker.latest_message)['text']}"
            )

    async def validate_slot_provider_ssn(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `slot_provider_ssn` value."""

        slot_provider_number_failure_count = tracker.get_slot("slot_provider_number_failure_count") or 0

        logging.debug("Inside validate_provider_ssn")
        logging.debug(f"IVR input SSN: {(tracker.latest_message)['text']}")

        number_ = re.sub(r"\D", "", str(tracker.latest_message["text"]))
        logging.debug(f"Pre-processed number: {number_}")

        # Retrieve matching records from the stored attribute
        matching_records = self.matching_records

        # Compare fetched records with user input
        try:
            if  matching_records and matching_records[0]["ssn"] == str(slot_value):
                # Proceed with validation
                return {
                    "slot_provider_ssn": slot_value,
                    "slot_provider_number_failure_count": slot_provider_number_failure_count,
                }
            
            else:
                if slot_provider_number_failure_count >= 2:
                    logging.debug(f"provider_ssn verification failed max tries")
                    # save_database_mongo(tracker, "provider_ssn", "N")
                    dispatcher.utter_message(response="utter_max_retries_exceeded")
                    return {
                        "slot_provider_number_failure_count": 0,
                        "slot_failure_flag": True,
                        "requested_slot":None
                    }
                else:
                    logging.debug(f"provider_ssn verification failed")
                    dispatcher.utter_message(
                    response="utter_invalid_SSN"
                    )
                    return {
                        "slot_provider_ssn": None,
                        "slot_provider_number_failure_count": slot_provider_number_failure_count + 1,
                    }
        except Exception as e:
            error_logger.error(
                f"index out of range error: {(tracker.latest_message)['text']}"
            )

    def validate_slot_provider_county(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `slot_provider_county` value."""
        slot_provider_number_failure_count = tracker.get_slot("slot_provider_number_failure_count") or 0

        logging.debug("Inside validate_provider_county")
        logging.debug(f"IVR input county: {(tracker.latest_message)['text']}")

        # Retrieve matching records from the stored attribute
        matching_records = self.matching_records

        # Compare fetched records with user input
        try:
            if  matching_records and matching_records[0]["county"] == str(slot_value):
                # Proceed with validation
                return {
                    "slot_provider_county": slot_value,
                    "slot_provider_number_failure_count": 0,
                }
            if slot_provider_number_failure_count >= 2:
                logging.debug(f"provider_county verification failed")

                dispatcher.utter_message(response="utter_invalid_county")
                return {
                    "slot_provider_number_failure_count": 0,
                    "slot_failure_flag": True,
                    "requested_slot": None,
                }
            else:
                logging.debug(f"provider_county verification failed")
                dispatcher.utter_message(response="utter_invalid_county")
                save_database_mongo(tracker, "provider_county", "N")
                return {
                    "slot_provider_county": None,
                    "slot_provider_number_failure_count": slot_provider_number_failure_count + 1,
                }
        except Exception as e:
            logging.debug(
                f"index out of range error: {(tracker.latest_message)['text']}"
            )
