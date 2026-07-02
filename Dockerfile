# DevOps Deployment Configuration for MatRisk Bond Risk Analytics Platform
# Day 15 Deliverable: Dockerfile

# Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MLFLOW_ALLOW_FILE_STORE=true

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (including compiler tools required for some ML packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
# Let's create requirements.txt programmatically
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all platform code and data files into the container
COPY . /app/

# Expose ports (e.g., 5000 for MLflow UI or 8501 for a Streamlit app if deployed later)
EXPOSE 5000
EXPOSE 8501

# Set the default command to run our test suite or portfolio analytics
CMD ["python", "portfolio_analytics.py"]
