# Dockerfile
FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "run.py"]
