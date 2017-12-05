#!/bin/sh
if [ ${ENV}="test" ]
then
    COMMAND="pserve"
else
    COMMAND="gunicorn --paste"
fi

/docker_entrypoint.sh && NEW_RELIC_CONFIG_FILE=/app/newrelic.ini newrelic-admin run-program ${COMMAND} /app/configs/"${ENV}".ini
