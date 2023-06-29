FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

RUN apk --update add postgresql-client

WORKDIR /migrator
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

ADD . ./
RUN chmod +x docker-entrypoint.sh
RUN chmod +x main.py

ENTRYPOINT ["./docker-entrypoint.sh"]
