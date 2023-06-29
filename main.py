#!/usr/bin/env python3

import sys
from colored import stylize, fg
import database
import migration_files


def check_for_inconsistent_db_state(migrations, migrations_to_apply):
    migrations_already_applied = [migration for migration in migrations if migration not in migrations_to_apply]

    if len(migrations_to_apply) == 0 or len(migrations_already_applied) == 0:
        return

    if migrations_to_apply[0] < migrations_already_applied[-1]:
        sys.stderr.write(f"Database in inconsistent state. Migration '{migrations_to_apply[0]}' not yet applied, "
                         f"but '{migrations_already_applied[-1]}' was already applied. "
                         f"Please apply this migration manually and re-run the migrator.")
        exit(-1)


def main():
    database.initialize()

    migrations = migration_files.get_available_migration_files_in_order()

    if len(migrations) == 0:
        print(f"Found no migrations")
        exit(0)

    print(f"Found {len(migrations)} migrations")

    database.add_migrations_information(migrations)
    migrations_to_apply = database.get_not_yet_applied_migrations()

    check_for_inconsistent_db_state(migrations, migrations_to_apply)

    migrations_to_apply = set(migrations_to_apply)

    for migration in migrations:
        print(f"Migration {migration}: ", end="")
        if migration not in migrations_to_apply:
            print(stylize("Already applied!", fg("blue")))
        else:
            migration_code = migration_files.get_migration_code(migration)
            database.apply_migration(migration, migration_code)
            print(stylize("Successfully applied!", fg('green')))


if __name__ == "__main__":
    main()
