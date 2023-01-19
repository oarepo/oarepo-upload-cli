pip install -e tests/model[tests]

# TODO: direnv

invenio index init --force
invenio db create

invenio run --cert test.crt --key test.key 2>&1 > tmp.error.log &
invenio_pid=$!

sleep 10

# requests
pytest tests/model_tests

kill $invenio_pid