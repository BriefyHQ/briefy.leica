#!/bin/sh
python3.5 -m http.server 8000 &
/docker_entrypoint.sh && NEW_RELIC_CONFIG_FILE=/app/newrelic-worker.ini newrelic-admin run-program worker