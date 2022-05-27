#!/usr/bin/env sh

while true
do
    "${1:-python}" -m poetry run python -m mcodingbot

    echo "Hit CTRL+C to stop..."
    sleep 5
done
