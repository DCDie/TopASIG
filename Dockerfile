FROM python:3.12-slim-bullseye AS build-venv

WORKDIR /usr/app

RUN python -m venv /usr/app/.venv
ENV PATH="/usr/app/.venv/bin:$PATH"

COPY pyproject.toml poetry.lock /usr/app/

RUN pip install poetry

RUN poetry install --no-root --no-dev

FROM python:3.12-slim-bullseye

WORKDIR /usr/app

RUN apt-get update &&  \
    apt-get install -y curl &&  \
    apt-get clean autoclean &&  \
    apt-get autoremove --purge -y &&  \
    rm -rf /var/lib/apt/lists/* &&  \
    rm -f /var/cache/apt/archives/*.deb &&  \
    find /var/lib/apt -type f | xargs rm -f &&  \
    find /var/cache -type f -exec rm -rf {} \; &&  \
    find /var/log -type f | while read f; do echo -ne '' > $f; done;


COPY --from=build-venv /usr/app/.venv /usr/app/.venv
ENV PATH="/usr/app/.venv/bin:$PATH"

COPY ./apps /usr/app/apps
COPY ./config /usr/app/config
COPY ./locale /usr/app/locale
COPY ./manage.py /usr/app
COPY ./gunicorn.conf.py /usr/app
COPY .env /usr/app

COPY ./docker-entrypoint.sh /usr/app

RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh

EXPOSE 8000

ENV DJANGO_ENV=environment

ENTRYPOINT ["/usr/app/docker-entrypoint.sh"]

CMD ["gunicorn"]

HEALTHCHECK --interval=5s --timeout=3s --retries=30 CMD curl -f http://localhost:8000/api/health/ || exit 1
