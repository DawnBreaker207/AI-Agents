FROM python:3.11-slim

# Prevent Python from writing pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace

WORKDIR /workspace

# Install optional system build tools (useful for compiling certain binary packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Expose API Port
EXPOSE 8888

# Launch backend FastAPI application
CMD ["python", "app/main.py"]
