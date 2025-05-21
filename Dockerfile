FROM python:3.12.10-slim-bookworm

WORKDIR /bot
COPY . /bot

# Install Python dependencies
RUN python -m pip install -r requirements.txt && \
	apt-get update && apt-get clean

# Ensure the .env file is included in the container
COPY .env /bot/.env

ENTRYPOINT [ "python", "bot.py" ]
