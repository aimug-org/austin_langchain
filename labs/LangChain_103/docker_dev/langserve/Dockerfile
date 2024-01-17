FROM python:3.11-slim

RUN pip install poetry==1.6.1

docker run -p 8000:8000 -it --rm --env-file ~/.env langchain-app bashRUN poetry config virtualenvs.create false

WORKDIR /code

#COPY ./pyproject.toml ./README.md ./poetry.lock* ./

#COPY ./packages ./packages

#RUN poetry install  --no-interaction --no-ansi --no-root

#COPY ./app ./app

#RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD exec uvicorn app.server:app --host 0.0.0.0 --port 8000
