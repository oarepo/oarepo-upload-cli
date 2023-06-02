#!/bin/bash
set -e

source '.env'

if [ -d .venv_test ]; then rm -rf .venv_test; fi
python3 -m venv .venv_test
source .venv_test/bin/activate
pip install -U pip setuptools wheel
pip install -e uct_theses

# TODO: direnv

export INVENIO_RECORDS_REFRESOLVER_CLS="invenio_records.resolver.InvenioRefResolver"
export INVENIO_RECORDS_REFRESOLVER_STORE="invenio_jsonschemas.proxies.current_refresolver_store"
export INVENIO_RATELIMIT_AUTHENTICATED_USER="200 per second"

invenio index destroy --yes-i-know --force
invenio index init --force

if [ -f .venv_test/var/instance/invenio.db ]; then rm -f .venv_test/var/instance/invenio.db; fi
invenio db create

invenio oarepo cf init
invenio oarepo fixtures load

invenio run --cert test.crt --key test.key 2>&1 > tmp.error.log &
invenio_pid=$!

sleep 10

pytest tests/model_tests

kill $invenio_pid
rm tmp.error.log