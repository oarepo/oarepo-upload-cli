#!/bin/bash


cd `dirname $0`/..

set -e

source .venv/bin/activate

python scripts/import_sample_data.py