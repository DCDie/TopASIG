# TopAsig API

**TopAsig API** is a Django-based project designed as a web API with integrated tools for handling RESTful requests,
OpenAPI documentation, and more.

## Features

- Built with **Django 5.1.4**.
- Exposes RESTful APIs using **Django REST Framework**.
- Integrated API documentation generation with **drf-spectacular**.
- Cross-Origin Resource Sharing (CORS) support via **django-cors-headers**.
- Dockerized deployment for simplified production readiness.
- Health checks for monitoring the service.

## Requirements

- Python 3.12 or higher
- Django 5.1.4
- Docker (optional but recommended for production deployment)

## Installation

1. Clone the repository:
    ```shell
    git clone <repository_url>
    cd asig
    ```

2. Install dependencies using `poetry`:
   ```shell
   pip install poetry
   poetry install
   ```

3. Run database migrations:
   ```shell
   python manage.py migrate
   ```

4. Start the development server:
   ```shell
   python manage.py runserver
   ```

5. Access the API at `http://127.0.0.1:8000`.

## Running in Docker

1. Build the Docker image:
   ```shell
   docker build -t asig-api .
   ```

2. Run the container:
   ```shell
   docker run -p 8000:8000 asig-api
   ```

3. Check the service's health status
   ```shell
   curl http://localhost:8000/api/health/
   ```

## Configuration

- The project uses **Gunicorn** as the WSGI HTTP server for production.
- Environment variables for customization:
    - `DJANGO_ENV`: Specifies the environment (e.g., development, production).
    - `GUNICORN_BIND`, `GUNICORN_WORKERS`, and others for Gunicorn.

## API Documentation

Documentation for the API is available at `/docs/`. This is automatically generated using **drf-spectacular**.

## Pre-commit Hooks

This project uses **pre-commit** with **Ruff** for linting and code formatting. To set up pre-commit hooks locally, run:

```shell
pre-commit install
```

You can also run the hooks manually:

```shell
pre-commit run --all-files
```

## Folder Structure

- `apps/`: Contains Django apps (`ensurance`, `common`, etc.).
- `config/`: Django project configuration files.
- `locale/`: Localization files.
- `templates/`: Django HTML templates.
- `manage.py`: Entry point for Django commands.

## License

This project is licensed under [MIT License](LICENSE).

## Author

**Daniel Cuznetov**
Email: daniel.cuznetov04@gmail.com