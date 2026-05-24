FROM python:3.11-slim

WORKDIR /app

# Install git (needed for cloning repos at runtime)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render provides PORT env var)
EXPOSE 10000

# Run the application directly with Python (NOT gunicorn!)
CMD ["python", "app.py"]
