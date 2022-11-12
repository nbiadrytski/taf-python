#!/bin/sh -x

ENV=$1
DR_ACCOUNT_HOST=$2
AUTH0_HOST=$3
RERUN=$4
CPUS=$5
GROUP=$6

cd self-service-api-tests || exit

pip install --upgrade pip
pip install -r requirements.txt

cd tests || exit

echo ""
echo "> Starting to run the tests"
echo ""

python -m pytest --app_host "$ENV" --dr_account_host "$DR_ACCOUNT_HOST" --auth0_host="$AUTH0_HOST" --reruns "$RERUN" \
-n "$CPUS" -m "$GROUP" --html=test_report.html --junitxml=junit_report.xml -s -v
