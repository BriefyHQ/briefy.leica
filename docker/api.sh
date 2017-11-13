#!/bin/sh
if [ ${ENV}="development" ]
then
    COMMAND="gunicorn --paste"
else
    COMMAND="pserve"
fi

/docker_entrypoint.sh && NEW_RELIC_CONFIG_FILE=/app/newrelic.ini newrelic-admin run-program ${COMMAND} /app/configs/"${ENV}".ini
