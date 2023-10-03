import logging
from flask import Flask, request, url_for
import os
from twilio.twiml.voice_response import VoiceResponse
import requests
from twilio.rest import Client

app = Flask(__name__)

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



@app.route("/favicon.ico")
def favicon():
    """
    Handles requests for the favicon.

    Returns:
        str: URL for the favicon.
    """
    return url_for("static", filename="data:,")


@app.route("/twilio/webhook", methods=["GET", "POST"])
def twilio_webhook():
    """
    Handles incoming Twilio webhook requests.

    Returns:
        list: An empty list as a response.
    """
    logging.debug(f"\n\n RASA listener :: {request} \n")

    # Uncomment to include a TwiML response
    # twiml_response = VoiceResponse()
    # twiml_response.say("How are you")
    logging.info("Done")
    return []


def send_to_rasa(call_sid, user_input):
    """
    Sends user input to the Rasa chatbot server and receives the response.

    Args:
        call_sid (str): The unique identifier for the call.
        user_input (str): The user's input message.

    Returns:
        dict: The response from the Rasa chatbot.
    """
    # Make a request to your Rasa chatbot server to get the response.
    # Replace 'http://localhost:5005/webhooks/rest/webhook' with your Rasa endpoint.

    rasa_url = "http://localhost:5005/webhooks/rest/webhook"

    rasa_payload = {"sender": call_sid, "message": user_input}
    response = requests.post(rasa_url, json=rasa_payload)
    logging.debug(f"\n Rasa response: {response.json()}")

    return response.json()[0]


if __name__ == "__main__":
    app.run(debug=True)
