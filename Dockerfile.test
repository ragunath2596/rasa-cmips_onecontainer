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

RUN chmod 777 cmips_nlu.sh

RUN ls -ltr && pwd

ENTRYPOINT ["/app/cmips_nlu.sh"]

EXPOSE 5005
