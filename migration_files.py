import os
import re
import sys

MIGRATION_FILE_NAME_REGEX = re.compile("\d{12}__\w+\.sql")

MIGRATION_FILES_PATH = os.environ.get("MIGRATION_FILES_PATH", "./migrations")

if not os.path.exists(MIGRATION_FILES_PATH):
    sys.stderr.write(f"Given migration files path '{MIGRATION_FILES_PATH}' doesn't exist")
    exit(-1)


def get_available_migration_files_in_order():
    files = os.listdir(MIGRATION_FILES_PATH)
    migration_files = [file for file in files if MIGRATION_FILE_NAME_REGEX.match(file)]
    migration_ids = [file[:-len(".sql")] for file in migration_files]
    return sorted(migration_ids)


def get_migration_code(migration_id):
    migration_file = f"{MIGRATION_FILES_PATH}/{migration_id}.sql"
    with open(migration_file, "r") as f:
        return f.read()
