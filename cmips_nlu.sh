#!/bin/bash

rasa run --enable-api --cors "*" --port 5005 --debug  --log-file nlu-debug.log
