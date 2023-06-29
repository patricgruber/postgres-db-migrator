#!/bin/sh

set -e

echo "Using database connection: postgresql://$DATABASE_USER:***@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME"

until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -c '\q' $DATABASE_NAME; do
  >&2 echo "Postgres is unavailable - waiting..."
  sleep 1
done

>&2 echo "Postgres is up - executing migrator"
exec "./main.py"
