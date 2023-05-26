
# Use an official Python runtime as the base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apache2 \
        apache2-dev \
        build-essential \
        libapache2-mod-wsgi-py3 \
        libpq-dev \
        netcat \
        libmariadb-dev \
        libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code into the container
COPY . .

RUN pip install gunicorn

# Collect static files
RUN python manage.py collectstatic --no-input


# Configure Apache
COPY myapp.conf /etc/apache2/sites-enabled/myapp.conf
RUN a2enmod rewrite

# Run database migrations
#RUN python manage.py migrate

# Expose port 80 for Apache
EXPOSE 80

# Start Apache in the foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
