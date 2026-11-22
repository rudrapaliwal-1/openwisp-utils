import runpy
import sys
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core import management


def check_pending_migrations(manage_py, app_labels):
    """Run the project's migration check against in-memory databases."""
    execute = management.execute_from_command_line

    def execute_with_isolated_databases(argv):
        # manage.py has selected the settings, but Django has yet to load apps.
        settings.DATABASES = {
            alias: {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
            for alias in settings.DATABASES
        }
        execute(argv)

    argv = [manage_py, "makemigrations", "--dry-run", "--check", *app_labels]
    import_path = [str(Path(manage_py).resolve().parent), *sys.path[1:]]
    with (
        patch.object(
            management, "execute_from_command_line", execute_with_isolated_databases
        ),
        patch.object(sys, "argv", argv),
        patch.object(sys, "path", import_path),
    ):
        runpy.run_path(manage_py, run_name="__main__")


if __name__ == "__main__":
    check_pending_migrations(sys.argv[1], sys.argv[2:])
