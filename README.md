# Wagtail SQLite Benchmark

Documented with [GitHub issues](https://github.com/tomkins/wagtail-sqlite-benchmark/issues?q=is%3Aissue).

Using [Bakery Demo](https://github.com/wagtail/bakerydemo) and [SQLite](https://www.sqlite.org/)
to see how Django and Wagtail perform using SQLite as a database.

## Running a benchmark

For all server and locust instructions - adjust the number of workers and users.

### Initial setup

```console
pip install -r requirements/production.txt
./manage.py migrate
./manage.py load_initial_data
./manage.py collectstatic --settings=bakerydemo.settings.production --noinput
```

### Gunicorn

```console
gunicorn \
    --env=DJANGO_SETTINGS_MODULE=bakerydemo.settings.production \
    --env=DJANGO_SECRET_KEY=demo \
    --workers=4 \
    bakerydemo.wsgi:application
```

### uWSGI

```console
uwsgi \
    --env=DJANGO_SETTINGS_MODULE=bakerydemo.settings.production \
    --env=DJANGO_SECRET_KEY=demo \
    --master \
    --http11-socket=127.0.0.1:8000 \
    --disable-logging \
    --workers=4 \
    --module=bakerydemo.wsgi
```

### Locust

```console
locust \
    --headless \
    --host http://127.0.0.1:8000 \
    --run-time 1m \
    --users 4
```
