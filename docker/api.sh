#!/bin/sh
/docker_entrypoint.sh && NEW_RELIC_CONFIG_FILE=/app/newrelic.ini newrelic-admin run-program pserve --paste /app/configs/"${ENV}".ini
