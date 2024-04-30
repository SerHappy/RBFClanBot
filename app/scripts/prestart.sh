#! /usr/bin/env sh

echo "Running alembic migrations"

# Let the DB start
sleep 10

# Run migrations
alembic upgrade head

echo "Finished running alembic migrations"
