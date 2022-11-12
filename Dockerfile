# https://github.com/microsoft/playwright/blob/master/utils/docker/Dockerfile.bionic
FROM mcr.microsoft.com/playwright:bionic

# Build params
ARG app_host
ARG dr_account_host
ARG auth0_host
ARG reruns
ARG cpus
ARG group_name
# Env vars params
ARG pendo_integration_key
ARG admin_api_key_staging
ARG admin_api_key_prod
ARG auth0_client_id
ARG auth0_client_secret
ARG auth0_client_id_prod
ARG auth0_client_secret_prod
ARG drap_admin_password_prod
ARG auth0_dev_client_id
ARG auth0_dev_client_secret
ARG auth0_prod_client_id
ARG auth0_prod_client_secret

# Set env vars
ENV PENDO_INTEGRATION_KEY=$pendo_integration_key
# app2
ENV ADMIN_API_KEY_STAGING=$admin_api_key_staging
ENV ADMIN_API_KEY_PROD=$admin_api_key_prod
# DRAP
ENV AUTH0_CLIENT_ID=$auth0_client_id
ENV AUTH0_CLIENT_SECRET=$auth0_client_secret
ENV AUTH0_CLIENT_ID_PROD=$auth0_client_id_prod
ENV AUTH0_CLIENT_SECRET_PROD=$auth0_client_secret_prod
ENV DRAP_ADMIN_PASSWORD_PROD=$drap_admin_password_prod
# auth0
ENV AUTH0_DEV_CLIENT_ID=$auth0_dev_client_id
ENV AUTH0_DEV_CLIENT_SECRET=$auth0_dev_client_secret
ENV AUTH0_PROD_CLIENT_ID=$auth0_prod_client_id
ENV AUTH0_PROD_CLIENT_SECRET=$auth0_prod_client_secret

COPY . /self-service-api-tests
WORKDIR /self-service-api-tests

RUN pip list
RUN pip install -r requirements.txt

RUN playwright install

RUN cd tests

# Run tests
# exit 0: always return a 0 (success) exit code
RUN python -m pytest \
    --app_host=$app_host \
    --dr_account_host=$dr_account_host \
    --auth0_host=$auth0_host \
    --reruns=$reruns \
    -n $cpus \
    -m $group_name \
    --html=test_report.html \
    --junitxml=junit_report.xml \
    -s -vv; exit 0
