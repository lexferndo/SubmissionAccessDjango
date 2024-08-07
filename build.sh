#!/bin/bash

# Build the project
echo "Creating virtual environment..."
python3 -m venv /venv
source /venv/bin/activate

echo "Building the project..."
pip install -r requirements.txt

echo "Make Migration..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collect Static..."
python manage.py collectstatic --noinput --clear