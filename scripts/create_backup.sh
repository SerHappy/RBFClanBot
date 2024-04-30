#!/bin/bash

set -a
source .env
set +a

DATE=$(date +%Y-%m-%d-%H-%M-%S)

BACKUP_PATH="${BACKUP_DIR:-./backups}"

if [ ! -d "$BACKUP_PATH" ]; then
    echo "Backup directory $BACKUP_PATH does not exist. Creating..."
    mkdir -p $BACKUP_PATH
fi

docker exec -t $DB_CONTAINER_NAME pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > "${BACKUP_PATH}/backup_${POSTGRES_DB}_${DATE}.sql.gz"

echo "Backup for $POSTGRES_DB completed on $DATE"
