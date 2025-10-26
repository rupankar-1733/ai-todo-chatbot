FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY app.py .

# Expose port
EXPOSE 7860

# Set environment variable to disable tokenizer warning
ENV TOKENIZERS_PARALLELISM=false

# Run the application
CMD ["python", "app.py"]
