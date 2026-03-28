web: cd backend && gunicorn pavilion_gemini.wsgi --bind 0.0.0.0:$PORT --timeout 120
release: cd backend && python manage.py migrate
