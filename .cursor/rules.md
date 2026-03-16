# Project Rules

This project uses Django with Docker and PostgreSQL.

## Python & Django

- Use Django class-based views whenever possible.
- Follow PEP8 coding style.
- Keep business logic inside models or service modules.
- Views should remain thin and only orchestrate HTTP logic.
- Avoid placing business logic inside templates.

## Project Structure

All domain apps are located inside:

src/applications/

Each app should contain:

- models.py
- views.py
- urls.py
- admin.py
- migrations/

## Frontend

- Use Django Templates.
- Use Bootstrap for styling.
- Reuse the global base template `base.html`.
- Avoid inline CSS unless necessary.

Templates should be located in:

templates/

or inside each Django app.

## Database

- Database: PostgreSQL
- ORM: Django ORM
- All schema changes must go through migrations.

Never modify the database schema manually.

## Docker

Development and production environments run inside Docker.

docker-compose files used:

- docker-compose.yml
- docker-compose.override.yml
- docker-compose.prod.yml

Management commands must run inside the Django container.

Example:

docker compose run web python manage.py migrate

## Git

- Use Git for version control.
- Avoid generating unnecessary files.
- Do not commit secrets or environment files.

## Static and Media

Static files:

/static/

Uploaded files:

/media/

Use `collectstatic` for production.