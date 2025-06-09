#!/bin/bash
set -e

if [ ! -d "/app/report/resources" ]; then
  echo "Папка resources не найдена в /app/report. Копирую дефолтные ресурсы..."
  cp -R /default_resources /app/report/resources
fi
exec "$@"
