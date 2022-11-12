#!/bin/sh -x

# Run the script with the below args
ENV=$1
DR_ACCOUNT_HOST=$2
AUTH0_HOST=$3
RERUN=$4
CPUS=$5
GROUP=$6

# Use standard docker instead of DR dockerwise
export DOCKERWISE_PASSTHROUGH=1

cd self-service-api-tests || exit

echo ""
echo "> Starting to build docker"
echo ""
docker build -t ui-tests \
--build-arg app_host="$ENV" \
--build-arg dr_account_host="$DR_ACCOUNT_HOST" \
--build-arg auth0_host="$AUTH0_HOST" \
--build-arg reruns="$RERUN" \
--build-arg cpus="$CPUS" \
--build-arg group_name="$GROUP" \
--build-arg pendo_integration_key="$PENDO_INTEGRATION_KEY" \
--build-arg admin_api_key_staging="$ADMIN_API_KEY_STAGING" \
--build-arg admin_api_key_prod="$ADMIN_API_KEY_PROD" \
--build-arg auth0_client_id="$AUTH0_CLIENT_ID" \
--build-arg auth0_client_secret="$AUTH0_CLIENT_SECRET" \
--build-arg auth0_client_id_prod="$AUTH0_CLIENT_ID_PROD" \
--build-arg auth0_client_secret_prod="$AUTH0_CLIENT_SECRET_PROD" \
--build-arg drap_admin_password_prod="$DRAP_ADMIN_PASSWORD_PROD" \
--build-arg auth0_dev_client_id="$AUTH0_DEV_CLIENT_ID" \
--build-arg auth0_dev_client_secret="$AUTH0_DEV_CLIENT_SECRET" \
--build-arg auth0_prod_client_id="$AUTH0_PROD_CLIENT_ID" \
--build-arg auth0_prod_client_secret="$AUTH0_PROD_CLIENT_SECRET" .

echo ""
echo "> Starting to run docker container"
echo ""
docker run -dt --name ui-tests ui-tests

echo ""
echo "> Coping files from docker to Jenkins after the tests are done"
echo ""
docker cp ui-tests:/self-service-api-tests .

echo ""
echo "> Stoping docker container"
echo ""
docker stop ui-tests

echo ""
echo "> Removing docker container"
echo ""
docker rm ui-tests
