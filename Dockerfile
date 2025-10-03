FROM python:3.11-slim

WORKDIR /app

# system deps for some packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r /app/backend/requirements.txt

# Copy the rest of the app
COPY . /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
