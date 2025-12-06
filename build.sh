# Render Build Script for Django
# https://render.com/docs/deploy-django

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
