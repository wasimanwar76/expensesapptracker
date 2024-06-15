# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential \
        default-libmysqlclient-dev \
        libpq-dev \
        pkg-config \
    && apt-get clean

# Set working directory in the container
WORKDIR /expensesapptracker

# Copy the current directory contents into the container at /expensesapptracker
COPY . /expensesapptracker/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run Django using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "expensesapptracker.wsgi:application"]
