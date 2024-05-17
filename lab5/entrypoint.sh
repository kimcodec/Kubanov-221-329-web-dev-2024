#!/bin/sh
echo "Waiting db to init...";
sleep 5;

./migrate -database $POSTGRESQL_URL -path migrations up

flask run --host 0.0.0.0 --port $APP_PORT