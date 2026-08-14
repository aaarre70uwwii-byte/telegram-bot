FROM python:3.10-slim

WORKDIR /app

# Copy dependency mappings
COPY requirements.txt .

# Install dependencies cleanly
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the main script directly (Do not use uvicorn/gunicorn unless building Webhooks)
CMD ["python", "main.py"]
