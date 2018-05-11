#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..


echo "Running pycodestyle"
pycodestyle django_datajsonar -v

echo "pycodestyle OK :)"
