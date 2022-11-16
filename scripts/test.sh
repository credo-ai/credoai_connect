#!/usr/bin/env bash

set -e
set -x

PYTHONPATH=. pytest --cov=connect --cov-report=term-missing tests "${@}"
