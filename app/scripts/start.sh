#! /usr/bin/env sh

set -e

if [ ! -f "/app/app/main.py" ]; then
    echo "Can't find main.py in /app/app/main.py"
    exit 1
fi

PRE_START_PATH=${PRE_START_PATH:-/app/app/scripts/prestart.sh}
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

poetry run python /app/app/main.py
