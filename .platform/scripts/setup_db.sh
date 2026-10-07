#!/bin/bash
# Build the SQLite database, load the sample polls and collect static files.
#
# Called from hooks/predeploy (app deployments, e.g. `eb deploy`) and from
# confighooks/predeploy (configuration changes, e.g. `eb setenv`). Both can
# replace the app directory with a fresh copy of the source bundle, which has
# no database, so the setup has to run in both cases.
set -eo pipefail

cd "$(dirname "$0")/../.."  # project root
source /var/app/venv/*/bin/activate

python3 manage.py migrate --noinput
python3 manage.py loaddata sample_polls
python3 manage.py collectstatic --noinput

# Hooks run as root, but the app runs as "webapp", which must be able to write
# the database (and its journal next to it) to record votes.
chown webapp:webapp . db.sqlite3
