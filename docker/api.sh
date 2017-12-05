#!/bin/sh
if [ "${ENV}" == "test" ];
then
    COMMAND="pserve"
else
    COMMAND="gunicorn --paste"
fi

export NEW_RELIC_CONFIG_FILE=/app/newrelic.ini

/docker_entrypoint.sh && newrelic-admin run-program ${COMMAND} /app/configs/"${ENV}".ini
