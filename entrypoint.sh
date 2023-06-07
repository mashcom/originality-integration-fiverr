#!/bin/bash
# entrypoint.sh

# Wait for MySQL to be ready
until nc -z -v -w30 db 3306
do
  echo "Waiting for MySQL to be ready..."
  sleep 5
done

# Run migrations and start Django server
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
