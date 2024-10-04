# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10.13-slim as prepare

# instalace curl, aby bylo mozne zprovoznit standardni healthcheck
RUN apt update && apt install curl -y && rm -rf /var/cache/apk/*

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

FROM prepare as test

COPY requirements-dev.txt .
RUN python -m pip install -r requirements-dev.txt

WORKDIR /app
COPY . /app

RUN python -m pytest --cov-report term-missing --cov=src tests/*

FROM prepare as runner
# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
WORKDIR /app
COPY . /app

RUN useradd appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--reload=True", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-t", "60", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
