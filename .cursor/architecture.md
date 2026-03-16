# System Architecture

The project is a modular Django monolith deployed using Docker containers.

## Directory Structure

src/
    config/              # Django project configuration
    applications/        # Domain apps

applications include:

- activity
- announcement
- blog
- diningRoom
- gallery
- history
- home
- news
- partner
- product
- tpv

Global directories:

templates/
static/
media/

## Template System

The frontend uses Django templates.

All pages extend from a global template:

base.html

Bootstrap is used for styling and layout.

## Database

Database engine: PostgreSQL.

The application interacts with the database using Django ORM.

Schema changes are handled through migrations.

## Docker Architecture

The project runs using Docker Compose.

Development configuration:

docker-compose.yml
docker-compose.override.yml

Production configuration:

docker-compose.prod.yml

Services include:

- Django application container
- PostgreSQL database container

Management commands must run inside containers.

## Deployment

Production deployment uses:

- Ubuntu Server
- Docker
- Nginx as reverse proxy
- Gunicorn as Django application server

Static files are served through Nginx.

## Version Control

The project uses Git for version control.

Repository includes:

- source code
- docker configuration
- requirements.txt