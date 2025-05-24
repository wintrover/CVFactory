# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=config.settings

# Add the current directory contents into the container at /app
COPY . /app

# Install uv globally in the container
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to the PATH
ENV PATH="/root/.local/bin:$PATH"

# Install any needed packages specified in requirements.txt using uv
# Make sure requirements.txt exists in your project root
RUN uv pip install --no-cache-dir --system -r requirements.txt
RUN mkdir -p /app/staticfiles

# django-compressor가 강제로 파일을 다시 압축하도록 함
RUN python manage.py compress --force

RUN python manage.py collectstatic --noinput -v 3

# Remove diagnostic print statements (no longer needed)
# RUN python manage.py shell -c "from django.conf import settings; print(f'DEBUG: STATIC_ROOT from Django settings: {settings.STATIC_ROOT}'); import os; print(f'DEBUG: Path {settings.STATIC_ROOT} exists: {os.path.exists(settings.STATIC_ROOT)}'); print(f'DEBUG: Path {settings.STATIC_ROOT} is directory: {os.path.isdir(settings.STATIC_ROOT)}')"

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"] 