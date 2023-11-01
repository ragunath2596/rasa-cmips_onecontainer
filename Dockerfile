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

RUN pre-commit install

RUN python3 -m spacy download en_core_web_md

RUN rasa train

COPY . .

RUN chmod 777 rasa.sh

ENTRYPOINT ["/app/rasa.sh"]

EXPOSE 5005 5055
