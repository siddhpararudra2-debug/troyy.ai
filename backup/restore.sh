#!/bin/bash
# Restore script for Database and Storage

echo "Engineering OS Restore Utility"
echo "------------------------------"

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <type> <file>"
    echo "type: 'db' or 'storage'"
    echo "file: path to the backup file (.sql.gz or .tar.gz)"
    exit 1
fi

TYPE=$1
FILE=$2

if [ ! -f "$FILE" ]; then
    echo "Error: File $FILE not found!"
    exit 1
fi

if [ "$TYPE" == "db" ]; then
    echo "Restoring database from $FILE..."
    
    # Load environment variables
    set -a
    source .env
    set +a
    
    if [ -z "$DATABASE_URL" ]; then
        echo "Error: DATABASE_URL not set in .env"
        exit 1
    fi
    
    # Decompress to temporary file
    TMP_FILE="/tmp/db_restore_$$.sql"
    gunzip -c "$FILE" > "$TMP_FILE"
    
    # Warning prompt
    read -p "WARNING: This will overwrite your existing database. Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        psql "$DATABASE_URL" < "$TMP_FILE"
        echo "Database restore completed."
    else
        echo "Restore aborted."
    fi
    
    rm "$TMP_FILE"
    
elif [ "$TYPE" == "storage" ]; then
    echo "Restoring storage from $FILE..."
    # Extract
    TMP_DIR="/tmp/storage_restore_$$"
    mkdir -p "$TMP_DIR"
    tar -xzf "$FILE" -C "$TMP_DIR"
    
    echo "Storage extracted to $TMP_DIR."
    echo "Please use AWS S3 CLI or a custom script to upload these files back to your Supabase buckets."
    echo "Example: aws s3 sync $TMP_DIR/<date>/cad-files s3://cad-files --endpoint-url https://your-project.supabase.co/storage/v1/s3"
    
    # In a full implementation, you'd script the AWS S3 sync back to the buckets here.
else
    echo "Invalid type. Use 'db' or 'storage'."
    exit 1
fi
