FROM python:3.11-alpine
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install pipenv
RUN pipenv install