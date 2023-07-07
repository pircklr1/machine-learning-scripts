FROM python:3.7-slim-buster

ENV PROJECT_ROOT /lsi-topic-modelling

WORKDIR $PROJECT_ROOT

RUN python -m pip install -U pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN python -m pipenv install --system

COPY . .

RUN python setup.py

EXPOSE 5000

ENTRYPOINT [ "gunicorn" ]
CMD ["-b", "0.0.0.0:5000", "--log-level=info", "-t", "900", "app:app"]
