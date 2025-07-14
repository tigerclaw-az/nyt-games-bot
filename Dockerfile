FROM python:3.12-slim

WORKDIR /app
COPY . /app
RUN touch /app/discord.log

RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential python3-dev && \
  apt-get clean

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel && \
  python -m pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "bot.py" ]
