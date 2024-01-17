FROM python:3.11-slim

RUN pip install poetry==1.6.1

RUN pip install google-api-python-client google-auth-oauthlib && \
    pip install pypdf2

RUN poetry config virtualenvs.create false

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/.credentials/keys.json

WORKDIR /code

COPY ./pyproject.toml ./langchain_template_README.md ./poetry.lock* ./

COPY ./packages ./packages

RUN poetry install  --no-interaction --no-ansi --no-root

COPY ./app ./app

RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD exec uvicorn app.server:app --host 0.0.0.0 --port 8000
