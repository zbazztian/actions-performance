#!/bin/sh
set -eu
pipenv run python3 perf.py "$@"
