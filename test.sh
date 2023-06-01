#!/bin/bash
source '.env'

pip install -e tests/model[tests]

# TODO: direnv

export INVENIO_RECORDS_REFRESOLVER_CLS="invenio_records.resolver.InvenioRefResolver"
export INVENIO_RECORDS_REFRESOLVER_STORE="invenio_jsonschemas.proxies.current_refresolver_store"
export INVENIO_RATELIMIT_AUTHENTICATED_USER="200 per second"

invenio index init --force
invenio db create

invenio run --cert test.crt --key test.key 2>&1 > tmp.error.log &
invenio_pid=$!

sleep 10

pytest tests/model_tests

kill $invenio_pid
rm tmp.error.log