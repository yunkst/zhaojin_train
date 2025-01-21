#!/usr/bin/env bash

set -e
set -x

pyright
ruff check
ruff format --check
