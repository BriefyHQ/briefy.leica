#!/usr/bin/env bash

newman -n 1 -c briefy.leica.postman_collection.json -e briefy.local.postman_environment.json --exitCode 1