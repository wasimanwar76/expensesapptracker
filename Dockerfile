# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean

# Set the working directory in the container
WORKDIR /expensesapptracker

# Copy the current directory contents into the container at /app
COPY . /expensesapptracker
COPY static /expensesapptracker/static  

# Create a virtual environment
RUN python -m venv /opt/venv

# Ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run Django using gunicorn, serving static files
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--chdir", "expensesapptracker", "expensesapptracker.wsgi:application"]
