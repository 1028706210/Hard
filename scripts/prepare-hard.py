"""Prepare the local database using the existing backed-up migration path."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "apps/api/src"))

from hard_api.backup.service import LocalBackupService
from hard_api.core.config import Settings
from hard_api.db.migrations import migrate_database

settings = Settings.from_environment(root)
migrate_database(
    settings.database_path,
    backup_provider=LocalBackupService(settings.backup_dir),
)
print(f"Database ready: {settings.database_path}")
