
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  && apt-get install -y libldap2-dev libsasl2-dev ldap-utils \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./django/requirements /requirements
RUN pip install -U pip
RUN pip install -U pip-tools \
  && pip-compile --annotate --quiet /requirements/base.in \
  && pip-compile --annotate --quiet /requirements/production.in

RUN pip install --no-cache-dir -r /requirements/production.txt \
  && rm -rf /requirements

#COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
#RUN sed -i 's/\r$//g' /entrypoint
#RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
COPY --chown=django:django ./django /app

USER django

WORKDIR /app
