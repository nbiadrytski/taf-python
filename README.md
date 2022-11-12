# Self Service API Tests

## Description
Self Service domain API-related tests

## Installation
Prerequisites

```console
Python 3.6 +
```

Clone the repository, make a separate virtualenv and install required packages and plugins

```console
1. git clone git@github.com:datarobot/self-service-api-tests.git
2. cd self-service-api-tests
3. pip install -r requirements.txt
```


## Usage
How to run tests locally:

```console
1. cd tests
2. python -m pytest --app_host=env --dr_account_host=env --auth0_host=env --reruns 1 -m trial -n 7 --junitxml=junit_report.xml --html=test_report.html -s -v
```

where 

`--app_host` environment to run AI Platform Trial tests against (e.g. `staging` or `prod`)

`--dr_account_host` environment to run DataRobot Account Portal tests against (e.g. `dr_account_staging`)

`--auth0_host` Auth0 environment, e.g. `auth0_dev`

`--reruns` Rerun failed tests n times

`-m` Run a group of tests. E.g `trial` (AI Platform Trial tests), `dr_account_portal` (DataRobot Account Portal tests)

`-n` (optional) number of CPUs to run tests in parallel. `auto` is for automatic detection of the number of CPUs

`--junitxml` (optional) path to a junit .xml test report

`--html` (optional) path to an index.html file of HTML report


The following environment variables need to be added to run _AI Platform Trial_ tests:
1. `ADMIN_API_KEY` PayAsYouGoUser admin api key

The following environment variables need to be added to run _DataRobot Account Self Service Portal_ tests:
1. `ADMIN_API_KEY` PayAsYouGoUser admin api key
2. `AUTH0_HOST` Auth0 domain, e.g. `https://datarobotdev.auth0.com`
3. `AUDIENCE_HOST` Auth0 audience domain, e.g. `https://staging.account.datarobot.com`
4. `AUTH0_CLIENT_ID` Auth0 client id
5. `AUTH0_CLIENT_SECRET` Auth0 client secret
6. `AUTH0_DEV_CLIENT_ID` Dev Auth0 client id
7. `AUTH0_DEV_CLIENT_SECRET` Dev Auth0 client secret

See [app settings](https://manage.auth0.com/dashboard/us/datarobotdev/applications/BZ6moDdghimn82uUvmDhjxaSowzYK3Z7/settings) for Auth0 details.

