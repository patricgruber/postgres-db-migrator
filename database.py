import os
import sys
from typing import Optional

import psycopg

DB_HOST = os.environ.get("DATABASE_HOST", "localhost")
DB_PORT = os.environ.get("DATABASE_PORT", "5432")
DB_NAME = os.environ.get("DATABASE_NAME", "postgres")
DB_USER = os.environ.get("DATABASE_USER", "postgres")
DB_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")

DB_CONN: Optional[psycopg.Connection] = None


def connect():
    global DB_CONN
    connection_url = get_connection_url()
    try:
        DB_CONN = psycopg.connect(connection_url)
    except Exception as e:
        secure_connection_url = connection_url.replace(f":{DB_PASSWORD}", ":***") if len(DB_PASSWORD) > 0 else connection_url
        sys.stderr.write(f"Couldn't connect to the database via '{secure_connection_url}':\n{e}\n")
        exit(-1)


def get_connection_url():
    password_part = f":{DB_PASSWORD}" if len(DB_PASSWORD) > 0 else ""
    return f"postgresql://{DB_USER}{password_part}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def initialize():
    connect()
    with DB_CONN.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id TEXT PRIMARY KEY,
                applied BOOLEAN DEFAULT FALSE
            );
        """)
    DB_CONN.commit()


def add_migrations_information(migrations):
    with DB_CONN.cursor() as cur:
        for migration in migrations:
            try:
                cur.execute("INSERT INTO schema_version (id) VALUES (%s)", (migration,))
            except psycopg.errors.UniqueViolation:
                DB_CONN.rollback()
            except Exception as e:
                sys.stderr.write(f"Error when inserting migration '{migration}':\n{e}\n")
                DB_CONN.close()
                exit(-1)
            DB_CONN.commit()


def get_not_yet_applied_migrations():
    with DB_CONN.cursor() as cur:
        try:
            rows = cur.execute("SELECT id FROM schema_version WHERE applied=false").fetchall()
        except Exception as e:
            sys.stderr.write(f"Error when fetching not yet applied migrations:\n{e}\n")
            DB_CONN.close()
            exit(-1)
        return sorted([row[0] for row in rows])


def apply_migration(migration_id, migration_text):
    with DB_CONN.cursor() as cur:
        try:
            cur.execute(migration_text)
        except Exception as e:
            sys.stderr.write(f"\nError when applying migration '{migration_id}':\n{e}\n")
            DB_CONN.close()
            exit(-1)
        try:
            cur.execute("UPDATE schema_version SET applied=true WHERE id=%s", (migration_id,))
        except Exception as e:
            sys.stderr.write(f"Error when setting '{migration_id}' as applied in the database:\n{e}\n")
            DB_CONN.close()
            exit(-1)
    DB_CONN.commit()
