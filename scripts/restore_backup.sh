#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE=$1

set -a
source .env
set +a

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file $BACKUP_FILE does not exist."
    exit 1
fi

echo "Restoring database from $BACKUP_FILE..."
gzip -dc $BACKUP_FILE | docker exec -i $DB_CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB

echo "Database restoration completed."
