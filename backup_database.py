from pathlib import Path
from datetime import datetime
import sqlite3


# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DB_PATH = BASE_DIR / "db.sqlite3"

# Backup directory
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


# Create timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Backup filename
BACKUP_PATH = BACKUP_DIR / f"db_backup_{timestamp}.sqlite3"


# Check database exists
if not DB_PATH.exists():
    print("ERROR: db.sqlite3 was not found.")
    exit(1)


# SQLite safe backup
source = sqlite3.connect(DB_PATH)
destination = sqlite3.connect(BACKUP_PATH)

try:
    with destination:
        source.backup(destination)

    print("Database backup created successfully!")
    print(f"Backup: {BACKUP_PATH}")

finally:
    destination.close()
    source.close()