# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=config.settings

# Add the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# Make sure requirements.txt exists in your project root
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/staticfiles

# Remove diagnostic print statements (no longer needed)
# RUN python manage.py shell -c "from django.conf import settings; print(f'DEBUG: STATIC_ROOT from Django settings: {settings.STATIC_ROOT}'); import os; print(f'DEBUG: Path {settings.STATIC_ROOT} exists: {os.path.exists(settings.STATIC_ROOT)}'); print(f'DEBUG: Path {settings.STATIC_ROOT} is directory: {os.path.isdir(settings.STATIC_ROOT)}')"

RUN python manage.py collectstatic --noinput -v 3

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 