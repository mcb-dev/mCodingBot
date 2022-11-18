#!/usr/bin/env sh

while true
do
    git pull
    "${1:-python}" -m poetry update
    "${1:-python}" -m poetry install
    "${1:-python}" -m poetry run python -m mcodingbot

    echo "Hit CTRL+C to stop..."
    sleep 5
done
