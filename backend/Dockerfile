# Use official Python 3.11 slim image — fully bypasses Render's version detection
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Render passes PORT as an env var; use shell form to expand it
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
