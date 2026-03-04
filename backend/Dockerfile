FROM python:3.11-slim

WORKDIR /app

# Install libmagic for python-magic file validation
RUN apt-get update && apt-get install -y libmagic1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .