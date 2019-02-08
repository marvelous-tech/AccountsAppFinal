FROM python:3.7

ADD Pipfile /Pipfile

RUN mkdir /code/
WORKDIR /code/
ADD . /code/

RUN pip install -U pipenv \
    && pipenv install --skip-lock

ENV DJANGO_SETTINGS_MODULE=settings_module.deploy
