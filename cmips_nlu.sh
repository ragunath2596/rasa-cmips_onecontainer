#!/bin/bash

# Start the Rasa actions server on port 5055
rasa run actions --port 5055 --debug &

# Start the Rasa NLU server on port 5005
rasa run --enable-api --cors "*" --port 5005 --debug --log-file nlu-debug.log
