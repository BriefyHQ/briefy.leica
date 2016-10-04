#!/bin/sh
/docker_entrypoint.sh && NEW_RELIC_CONFIG_FILE=/app/newrelic.ini newrelic-admin run-program /usr/local/bin/gunicorn --paste /app/configs/"${ENV}".ini
