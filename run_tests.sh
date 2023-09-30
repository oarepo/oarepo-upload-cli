#!/bin/bash

set -e

cd "$(dirname "$0")"

initialize_venv() {
    if [ -d .venv ] ; then
      return
    fi

    python3 -m venv .venv

    .venv/bin/pip install -U setuptools pip wheel
    .venv/bin/pip install -e ".[tests]"
}

initialize_server_venv() {

  if [ -d .venv-server ] ; then
    return
  fi

  python3 -m venv .venv-server
  source .venv-server/bin/activate

  .venv-server/bin/pip install -U setuptools pip wheel
  .venv-server/bin/pip install -e simple-server
}

initialize_builder_venv() {

  if [ -d .venv-builder ] ; then
    return
  fi

  python3 -m venv .venv-builder
  source .venv-builder/bin/activate

  .venv-builder/bin/pip install -U setuptools pip wheel
  .venv-builder/bin/pip install oarepo-model-builder oarepo-model-builder-files
}

create_server() {
  initialize_builder_venv

  if [ -d simple-server ] ; then
    return
  fi

  .venv-builder/bin/oarepo-compile-model tests/model.yaml --output-directory simple-server -vvv
}

start_server() {
  (
    initialize_server_venv

    source .venv-server/bin/activate
    if [ ! -d .venv-server/var/instance ] ; then
      mkdir -p .venv-server/var/instance
    fi
    cat <<EOF >.venv-server/var/instance/invenio.cfg
RECORDS_REFRESOLVER_CLS="invenio_records.resolver.InvenioRefResolver"
RECORDS_REFRESOLVER_STORE="invenio_jsonschemas.proxies.current_refresolver_store"
RATELIMIT_AUTHENTICATED_USER="200 per second"
FILES_REST_DEFAULT_STORAGE_CLASS="L"
FILES_REST_STORAGE_CLASS_LIST = {
    "L": "Local",
    "F": "Fetch",
    "R": "Remote",
}

RATELIMIT_GUEST_USER = "5000 per hour;500 per minute"
RATELIMIT_AUTHENTICATED_USER = "200000 per hour;2000 per minute"

EOF

    invenio db destroy --yes-i-know || true
    invenio db create
    invenio index destroy --yes-i-know || true
    invenio index init --force
    invenio files location create --default default file:simple-server/files

    invenio users create -a -c test@test.com --password testtest
    invenio tokens create -n test -u test@test.com >.token

    (
      invenio run --cert test.crt --key test.key  2>&1 &
      echo "$!" >.invenio.pid
    ) | tee tmp.error.log &
    echo "Waiting for server to start"
    sleep 5
  )
}

stop_server() {
  if [ -f .invenio.pid ] ; then
    kill "$(cat .invenio.pid)" || true
    sleep 2
    kill -9 "$(cat .invenio.pid)" || true
    rm .invenio.pid
  fi
}

create_server

if [ "$1" == "--create" ] ; then
  exit 0
fi

# start server and schedule cleanup
start_server
trap stop_server EXIT

if [ "$1" == "--server" ] ; then
  echo "Running at https://127.0.0.1:5000/api/simple/. Press enter to stop the server"
  read -r
  exit 0
fi


# initialize virtualenv and perform tests
echo "Running tests"
initialize_venv
source .venv/bin/activate
pytest tests

stop_server &>/dev/null

echo "All tests succeeded"
