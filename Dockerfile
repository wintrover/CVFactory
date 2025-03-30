FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4

# Install Chrome and Firefox
RUN apt-get update && apt-get install -y \
    chromium \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create log directory
RUN mkdir -p logs

# Set environment variables for headless browser
ENV PYTHONUNBUFFERED=1
ENV SELENIUM_DRIVER_EXECUTABLE_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 