# Postgres DB-Migrator

This simple script/container handles migrations in a Postgres database.
It will check which version the database is currently in and will then execute the migrations needed to migrate it to the newest version.

It uses the following environment variables as configuration:
- `DATABASE_HOST`: database hostname (default: `localhost`)
- `DATABASE_PORT`: port number of the opened socket for the database connection (default: `5432`)
- `DATABASE_NAME`: database name (default: `postgres`)
- `DATABASE_USER`: database username (default: `postgres`)
- `DATABASE_PASSWORD`: password of the database user (default: ``)
- `MIGRATION_FILES_PATH`: the path to the directory that_ contains all the migration scripts (default: `./migrations`)

Migration scripts have to have the following format: `YYYYMMDDHHMM__<name>.sql`, where name is a string of unicode word characters like [a-zA-Z0-9_].
This format is used to determine the correct order in which the migration scripts are supposed to be executed. Files that do not follow this format will be ignored. If the database is in an inconsistent state (a newer migration has been executed, but an older one wasn't applied yet), the migrator exits and prints which migration needs to be applied manually, which includes running the actual migration and setting updating the state in the `schema_version` table with `UPDATE schema_version SET applied = true WHERE id = '<migration-id>'`.
The `migration-id` is the file name without the `.sql` ending.

The `docker-entrypoint.sh` waits for the database to be running before trying to execute the migrations.

## Running without Docker
- Setup a virtual environment with `python -m venv venv`
- Activate the virtual environment with `source ./venv/activate`
    - This is only when using `bash`, for other shells check the documentation [How venvs work - Python documentation](https://docs.python.org/3/library/venv.html#how-venvs-work)
- Install the requirements with `python -m pip install -r requirements.txt`
- Run the script and set the environment variables: `DATABASE_HOST=db DATABASE_PORT=5432 DATABASE_NAME=postgres DATABASE_USER=user DATABASE_PASSWORD=password MIGRATIONS_FILES_PATH=/local/path/to/migrations/ ./main.py`

## Running with Docker
- Build the docker container with: `docker build -t postgres-db-migrator .`
- Run the docker container with: `docker run -e DATABASE_HOST=db -e DATABASE_PORT=5432 -e DATABASE_NAME=postgres -e DATABASE_USER=user -e DATABASE_PASSWORD=password -e MIGRATIONS_FILES_PATH=/migrations -v /local/path/to/migrations/:/migrations postgres-db-migrator`

## Running with docker-compose
Add the database migrator in the services section of the `docker-compose.yml` file like this:
```
db-migrator:
    build:
      context: .
      dockerfile: Dockerfile
    restart: "no"
    environment:
      - MIGRATION_FILES_PATH=/migrations
      - DATABASE_HOST=database
      - DATABASE_PORT=5432
      - DATABASE_NAME=postgres
      - DATABASE_USER=user
      - DATABASE_PASSWORD=password
    volumes:
      - /local/path/to/migrations/:/migrations
```
Execute it by running `docker-compose up -d` to run it in the background with the other services. If you want to only run the migrations and get the ouput you can executed `docker-compose up database -d && docker-compose up db-migrator`. This starts the database in the background and the database migrator in the foreground.