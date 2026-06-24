#!/bin/bash
# Script to backup Supabase PostgreSQL Database

# Load environment variables (ensure .env exists with DB credentials)
set -a
source .env
set +a

# Configuration
BACKUP_DIR="./backups/db"
DATE=$(date +"%Y%m%d_%H%M%S")
FILENAME="engineering_os_db_backup_$DATE.sql"
MAX_BACKUPS=7

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting database backup to $BACKUP_DIR/$FILENAME..."

# Run pg_dump (requires PostgreSQL client tools)
# Replace connection string or components via env vars
# DATABASE_URL should be set in .env
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set."
    exit 1
fi

pg_dump "$DATABASE_URL" --clean --if-exists --no-owner --no-privileges > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    echo "Backup completed successfully."
    
    # Compress the backup
    gzip "$BACKUP_DIR/$FILENAME"
    echo "Backup compressed: $BACKUP_DIR/$FILENAME.gz"
    
    # Clean up old backups keeping only MAX_BACKUPS
    echo "Cleaning up old backups (keeping last $MAX_BACKUPS)..."
    ls -t "$BACKUP_DIR"/engineering_os_db_backup_*.sql.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
else
    echo "Backup failed!"
    exit 1
fi
