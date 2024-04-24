#!/bin/sh
echo "Waiting db to init...";
sleep 5;

export DB_USER='postgres'; export DB_PASSWORD='postgres';
export DB_HOST='postgres'; export DB_NAME='postgres'; export DB_PORT='5432';
export POSTGRESQL_URL=postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME?sslmode=disable;

./migrate -database $POSTGRESQL_URL -path migrations up

python app.py