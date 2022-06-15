#!/usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

echo "Fetching the latest crowdin-cli"
docker pull crowdin/cli >/dev/null 2>&1

echo "Sending sources to crowdin"
docker run --rm -v ${SCRIPT_PATH}/crowdin.yml:/crowdin.yml -v ${SCRIPT_PATH}/project/pyha/locale:/project/pyha/locale crowdin/cli \
 crowdin upload sources -c /crowdin.yml

echo "Fetching translations from crowdin"
docker run --rm -v ${SCRIPT_PATH}/crowdin.yml:/crowdin.yml -v ${SCRIPT_PATH}/project/pyha/locale:/project/pyha/locale crowdin/cli \
 crowdin download -c /crowdin.yml

echo "All done"
