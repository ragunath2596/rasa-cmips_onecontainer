FROM python:3.8

WORKDIR /app

COPY ./ /app

RUN apt update && apt install pre-commit  -y

RUN pip install -r requirements.txt

RUN cd /usr/local/lib/python3.8/site-packages/rasa/core/channels && \
    mv twilio_voice.py twilio_voice.py.old && \
    cp /app/utils/twilio_voice.py . && \
    ls -ltr && \
    cd /app

#RUN pip install -r requirements-dev.txt

RUN pre-commit install

RUN python3 -m spacy download en_core_web_md

#RUN python3 -m spacy link en_core_web_md en

RUN rasa train

COPY . .

# Set execute permissions for your scripts
RUN chmod 777 cmips_actions.sh
RUN chmod 777 cmips_nlu.sh

# Train your Rasa models
RUN rasa train

# Expose the necessary ports
EXPOSE 5055
EXPOSE 5005

# Define the entry point for your application
CMD ["/app/cmips_onecontainer.sh"]
