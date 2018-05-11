#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
# -f parseable
pylint django_datajsonar --rcfile=.pylintrc
echo "pylint OK :)"
