FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-parler.txt .
RUN pip install --no-cache-dir -r requirements-parler.txt

COPY . .
RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/output

EXPOSE 8000

CMD ["uvicorn", "podcast_playground.api:app", "--host", "0.0.0.0", "--port", "8000"]
