# Base image with Python (Slim version)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /home/defensive-eye

# Install system dependencies (Including OpenCV dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
COPY requirements.txt /home/defensive-eye/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /home/defensive-eye/
