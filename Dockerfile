FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-parler.txt .
RUN pip install --no-cache-dir -r requirements-parler.txt

COPY . .
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["python", "-m", "podcast_playground"]
