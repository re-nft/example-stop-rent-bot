FROM python:3.11 as python-base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV POETRY_VERSION=1.4.2
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV PYSETUP_PATH="/opt/pysetup"
ENV VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

WORKDIR /bot
COPY poetry.lock pyproject.toml /bot/

RUN poetry install --no-dev

COPY bot/__init__.py ./bot/
COPY bot/logs.py ./bot/
COPY bot/main.py ./bot/
COPY bot/abi.py ./bot/
COPY bot/diskord.py ./bot/
COPY bot/renting.py ./bot/
COPY bot/secrets.py ./bot/
COPY bot/consts.py ./bot/

ENV PATH="/bot/.venv/bin:$PATH"

ENTRYPOINT ["poetry", "run", "python", "-m", "bot.main"]
