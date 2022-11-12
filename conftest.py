import logging
from time import time
from datetime import datetime

from time import sleep

import requests
from dictdiffer import diff
from pytest import (
    fixture,
    skip
)

from utils.errors import NoHostArgException
from utils.helper_funcs import (
    get_host,
    user_identity,
    time_left,
    is_iso_date_valid,
    insert_into_str,
    get_value_by_json_path,
    utc_to_iso,
    convert_json_to_dict
)
from utils.clients import (
    AppClient,
    DrAccountPortalClient,
    Auth0Client,
    DocsPortalClient
)
from utils.http_utils import ResponseHandler
from utils.constants import (
    ERROR_TEXT_NOT_IN_RESP,
    ERROR_TEXT_IN_RESP,
    APP_HOST_ARG,
    DR_ACCOUNT_HOST_ARG,
    STATUS_ERROR_TEXT,
    ERROR_JSON_RESP,
    AUTH0_HOST_ARG,
    ERROR_JSON_KEY,
    LIMITED_ACCESS_RESP_CODE,
    LIMITED_ACCESS_ERROR_CODE,
    LIMITED_ACCESS_MESSAGE,
    NF_ERROR_TEXT,
    PORTAL_ID_KEY,
    TIMEOUT_MESSAGE
)
from utils.data_enums import (
    DeploymentActionLogKeys,
    NfKeys,
    Envs
)


LOGGER = logging.getLogger(__name__)


def pytest_addoption(parser):
    """
    Adds command line args.

    Parameters
    ----------
    parser : Parser
        Parser for command line arguments
    """
    parser.addoption(
        APP_HOST_ARG, action='store', help='App host')
    parser.addoption(
        DR_ACCOUNT_HOST_ARG, action='store', help='DataRobot Account Portal host')
    parser.addoption(
        AUTH0_HOST_ARG, action='store', help='Auth0 host')


@fixture(scope='session')
def session():
    """
    Returns requests.sessions.Session() object.

    Returns
    -------
    session object : requests.sessions.Session
        HTTP session
    """
    return requests.Session()


@fixture(scope='session')
def app_host(request):
    """
    Returns --app_host command line arg value: see Envs app2 hosts in utils.data_enums.
    Raises NoHostArgException if --app_host command line arg was not passed.

    Parameters
    ----------
    request : FixtureRequest
        Special fixture providing information of the requesting test function

    Returns
    -------
    app host : str
        Value of --app_host command line arg
    """
    if request.config.getoption(APP_HOST_ARG) is None:
        raise NoHostArgException(
            request.config.getoption(APP_HOST_ARG), APP_HOST_ARG
        )
    return request.config.getoption(APP_HOST_ARG)


@fixture(autouse=True)
def skip_test_by_env(request, app_host):
    """
    Skip running a test by passed env value, e.g. prod.
    Apply to test function: @mark.skip_if_env('prod')

    Parameters
    ----------
    request : FixtureRequest
        Special fixture providing information of the requesting test function
    app_host : function
        Returns application hostname, e.g. prod
    """
    if request.node.get_closest_marker('skip_if_env'):
        if request.node.get_closest_marker('skip_if_env').args[0] == app_host:
            skip(f'This test should not run at "{app_host}" env.')


def pytest_configure(config):
    """
    Adds skip_if_env marker to pytest config.

    Parameters
    ----------
    config : Config
        Access to configuration values, plugin manager and plugin hooks
    """
    config.addinivalue_line(
        'markers',
        'skip_test_by_env(app_host): skip running a test for the passed env',)


def pytest_collection_modifyitems(items):
    """
    Automatically adds 'all' mark to all test functions.
    'all' mark is used to run all tests.
    -m mark_name
    -m "mark_name or mark_name or mark_name" to pass several marks.
    """
    for item in items:
        item.add_marker('all')


@fixture(scope='session')
def dr_account_host(request):
    """
    Returns DR Account Portal --dr_account_host command line arg value:
    see Envs DataRobot Account Portal hosts in utils.data_enums.
    Raises NoHostArgException if --dr_account_host command line arg was not passed.

    Parameters
    ----------
    request : FixtureRequest
        Special fixture providing information of the requesting test function

    Returns
    -------
    dr_account_host : str
        DR Account Portal --dr_account_host command line arg value
    """
    if request.config.getoption(DR_ACCOUNT_HOST_ARG) is None:
        raise NoHostArgException(
            request.config.getoption(DR_ACCOUNT_HOST_ARG), DR_ACCOUNT_HOST_ARG)

    return request.config.getoption(DR_ACCOUNT_HOST_ARG)


@fixture(scope='session')
def auth0_host(request):
    """
    Returns Auth0 --auth0_host command line arg value: see Envs Auth0 hosts in utils.data_enums.
    Raises NoHostArgException if --auth0_host command line arg was not passed.

    Parameters
    ----------
    request : FixtureRequest
        Special fixture providing information of the requesting test function

    Returns
    -------
    dr_account_host : str
        Auth0 --auth0_host command line arg value
    """
    if request.config.getoption(AUTH0_HOST_ARG) is None:
        raise NoHostArgException(request.config.getoption(AUTH0_HOST_ARG), AUTH0_HOST_ARG)

    return request.config.getoption(AUTH0_HOST_ARG)


@fixture(scope='session')
def env_params(app_host, dr_account_host, auth0_host):
    """
    Returns app host, DRAP and Auth0 hosts passed as command line args.

    Parameters
    ----------
    app_host : function
        Returns application hostname, e.g. https://staging.datarobot.com
    dr_account_host : function
        Returns DR Account Portal host, e.g. https://draccount-staging.ent.datarobot.com/
    auth0_host : function
        Returns Auth0 host, e.g. https://datarobotdev.auth0.com

    Returns
    -------
    app host, dr_account_host, auth0_host : tuple
        Tuple of app, DR Account Portal and Auth0 hosts values
    """
    application_host = get_host(app_host)
    account_host = get_host(dr_account_host)
    auth0_host = get_host(auth0_host)

    LOGGER.info('App host: %s', application_host)
    LOGGER.info('DataRobot Account Portal host: %s', account_host)
    LOGGER.info('Auth0 host: %s', auth0_host)

    return application_host, account_host, auth0_host


@fixture(scope='session')
def app_client(env_params, session):
    """
    Returns AppClient object to perform internal, api/v2 or DR client API actions.

    Parameters
    ----------
    env_params : function
        Returns app host and admin's API key tuple
    session : function
        Returns <requests.sessions.Session> object

    Returns
    -------
    app_client : AppClient
        App client object
    """
    return AppClient(env_params, session)


@fixture(scope='session')
def auth0_client(env_params, session):
    """
    Returns Auth0Client object to perform Auth0 actions.

    Parameters
    ----------
    env_params : function
        Returns app host and admin's API key tuple
    session : function
        Returns <requests.sessions.Session> object

    Returns
    -------
    app_client : Auth0Client
        Auth0Client client object
    """
    return Auth0Client(env_params, session)


@fixture(scope='session')
def docs_client(env_params, session):
    """
    Returns DocsPortalClient object to perform Docs Portal actions.

    Parameters
    ----------
    env_params : function
        Returns app2, DRAP and Auth0 hosts.
    session : function
        Returns <requests.sessions.Session> object

    Returns
    -------
    docs_client : DocsPortalClient
        DocsPortalClient client object
    """
    return DocsPortalClient(env_params, session)


@fixture
def identity():
    """
    Returns username, first_name and last_name according to the format set in user_identity() helper func.

    Returns
    -------
    username, first_name, last_name : tuple
        Username, first_name and last_name
    """
    return user_identity()


@fixture
def user_setup_and_teardown(identity, app_client):
    """
    Performs PayAsYouGoUser set up and tear down.
    1. Creates PayAsYouGoUser without Auth0 account
    2. PayAsYouGoUser opens invite link to sign up
    3. PayAsYouGoUser signs up
    4. PayAsYouGoUser's API key is created
    5. Stores user_id, username, first_name, last_name
    6. Delete PayAsYouGoUser as tear down

    Parameters
    ----------
    app_client : function
        Returns AppClient object
    identity : function
        Returns username, first_name and last_name
    """
    username, first_name, last_name = identity
    user_id = app_client.setup_self_service_user(
        username, first_name, last_name
    )
    yield user_id, username, first_name, last_name

    app_client.v2_delete_payg_user(user_id)


@fixture
def payg_drap_user_setup_teardown(env_params, app_client,
                                  dr_account_client, auth0_client):

    # Create and sign up PayAsYouGoUser
    username, first_name, last_name = user_identity()

    # Create and sign up PayAsYouGoUser
    # If prod, create Auth0 account as well
    if Envs.PROD.value in env_params[0]:
        user_id = app_client.setup_self_service_user(
            username, first_name, last_name, link_dr_account=True
        )
    else:  # don't create Auth0 account if staging
        user_id = app_client.setup_self_service_user(
            username, first_name, last_name,
        )
    # Register DRAP user
    dr_account_client.register_user(
        username, first_name, last_name
    )
    payload = {
        PORTAL_ID_KEY: dr_account_client.portal_id,
        'admin': False,
        'creditsUser': True
    }
    # Add creditsUser role to DRAP user
    dr_account_client.admin_update_role(payload)

    yield app_client, user_id, username, first_name, last_name

    # Delete PayAsYouGoUser
    app_client.v2_delete_payg_user(user_id)
    # Delete DRAP user
    dr_account_client.delete_user(dr_account_client.portal_id)
    # Delete Auth0 user if prod
    if Envs.AUTH0_PROD.value in env_params[2]:
        auth0_client.delete_auth0_user(username)


@fixture(scope='session')
def dr_account_client(env_params, session):
    """
    Returns DrAccountPortalClient object to perform DR Account Portal user actions.

    Parameters
    ----------
    env_params : function
        Returns app host, admin's API key, DR Account host tuple
    session : function
        Returns <requests.sessions.Session> object

    Returns
    -------
    dr_account_client : DrAccountPortalClient
        DrAccountPortalClient client object
    """
    return DrAccountPortalClient(env_params, session)


@fixture
def status_code():
    """
    Returns a function which returns a status code
    of the passed Response using ResponseHandler object.

    Returns
    -------
    status_code_ : function
        Function which returns HTTP status code
    """
    def status_code_(resp):
        return ResponseHandler(resp).get_status_code()

    return status_code_


@fixture
def resp_json():
    """
    Returns a function which returns a json-encoded content
    of the passed Response object using ResponseHandler object.

    Returns
    -------
    resp_json_ : function
        Function which returns a json-encoded content of Response
    """
    def resp_json_(resp):
        return ResponseHandler(resp).get_json()

    return resp_json_


@fixture
def resp_text():
    """
    Returns a function which returns text content
    of the passed Response object using ResponseHandler object.

    Returns
    -------
    resp_text_ : function
        Function which returns text content of Response
    """
    def resp_text_(resp):
        return ResponseHandler(resp).get_text()

    return resp_text_


@fixture
def resp_content():
    """
    Returns a function which returns response content in bytes.

    Returns
    -------
    resp_content_ : function
        Function which returns bytes content of Response
    """
    def resp_content_(resp):
        return ResponseHandler(resp).get_content()

    return resp_content_


@fixture
def setup_project(app_client):
    """
    Creates a project from file and sets a target.

    Parameters
    ----------
    app_client : function
        Returns AppClient object

    Returns
    -------
    project_setup_ : function
        Function to create a project from file and set a target
    """
    def project_setup_(dataset_path, target):

        project_id = app_client.v2_create_project_from_file(dataset_path)
        app_client.set_target(target, project_id)
        return project_id

    return project_setup_


@fixture
def teardown_project(app_client):
    """
    Tear down fixture to delete a project.

    Parameters
    ----------
    app_client : function
        Returns AppClient object
    """
    yield
    app_client.v2_delete_project()


@fixture
def get_value_from_json_response():
    """
    Returns a function which returns a value of the json path key
    from json_keys_config using ResponseHandler object.

    Returns
    -------
    get_value_from_json_response_ : function
        Value of the json path key from json_keys_config
    """

    def get_value_from_json_response_(resp, value):
        return ResponseHandler(resp).get_json_key_value(value)

    return get_value_from_json_response_


@fixture
def make_single_predictions(app_client, resp_json):
    """
    Makes single predictions.

    Parameters
    ----------
    app_client : function
        Returns AppClient object
    resp_json : function
        Returns json-encoded content of response

    Returns
    -------
    make_single_predictions_ : function
        Returns predictions response
    """
    def make_single_predictions_(deployment_id, dataset, expected_rows):

        predictions = app_client.make_predictions(deployment_id, dataset)
        predictions_rows = len(resp_json(predictions)['data'])

        assert predictions_rows == expected_rows, \
            f'Got {predictions_rows} predictions rows, expected: {expected_rows}'

        return predictions

    return make_single_predictions_


@fixture
def deploy_automodel(app_client):
    """
    Starts Automodel deployment and waits until it's deployed.

    Parameters
    ----------
    app_client : function
        Returns AppClient object

    Returns
    -------
    deploy_automodel_ : function
        Returns Automodel deployment id
    """
    def deploy_automodel_(
            label, project_id, description='', has_description=True):

        # start Automodel deployment
        app_client.v2_deploy_automodel(label, project_id, description, has_description)
        # wait until Automodel is deployed
        return app_client.v2_poll_for_first_available_deployment()

    return deploy_automodel_


@fixture
def is_model_replaced(app_client, get_value_from_json_response):
    """
    Returns if a deployed model was replaced n times or polling timed out.
    Poll until 'count' key from GET api/v2/deployments/{deployment_id}/actionLog/
    returns replaced_count + 2 (which means a model was replaced 2 times)
    or times out in timeout_period minutes.

    Parameters
    ----------
    app_client : function
        Returns AppClient object
    get_value_from_json_response : function
        Returns json-encoded content of response

    Returns
    -------
    poll_for_model_replaced : function
        Returns if a deployed model was replaced n times or polling timed out
    """
    def poll_for_model_replaced(deployment_id, replaced_count=1,
                                timeout_period=20, poll_interval=1):

        timeout = time() + 60 * timeout_period  # timeout_period minutes from now
        while True:
            action_log = app_client.v2_deployments_action_log(deployment_id)
            LOGGER.info(
                'Polling for model with deployment_id %s to be replaced %d time(s). '
                'Will stop polling in: %s',
                deployment_id, replaced_count, time_left(timeout))

            if time() > timeout:
                LOGGER.error(
                    'Model with deployment_id %s was not replaced %d time(s). '
                    'Timed out after %d minutes',
                    deployment_id, replaced_count, timeout_period
                )
                return False

            if get_value_from_json_response(
                    action_log, DeploymentActionLogKeys.COUNT.value) == replaced_count + 2:
                LOGGER.info(
                    'Model with deployment_id %s has been replaced %d time(s)',
                    deployment_id, replaced_count
                )
                return True

            sleep(poll_interval)

    return poll_for_model_replaced


@fixture
def is_model_job_done(app_client, resp_text):
    """
    Returns if a model job finished running or polling timed out.
    Polls until model_name is absent in GET api/v2/projects/{pid}/modelJobs/ response

    Parameters
    ----------
    app_client : function
        Returns AppClient object
    resp_text : function
        Returns response as unicode text

    Returns
    -------
    poll_for_model_job_to_finish : function
        Returns if a model job finished running or polling timed out
    """
    def poll_for_model_job_to_finish(project_id, model_name,
                                     timeout_period=10, poll_interval=1):

        timeout = time() + 60 * timeout_period  # timeout_period minutes from now
        while True:
            LOGGER.info('Polling for %s model job to finish. '
                         'Will stop polling in: %s', model_name, time_left(timeout))
            if time() > timeout:
                LOGGER.error('%s model job is did not finish. '
                             'Timed out after %d minutes', model_name, timeout_period)
                return False

            if model_name not in resp_text(app_client.v2_get_model_jobs(project_id)):
                LOGGER.info(
                    '%s model job is finished', model_name
                )
                return True

            sleep(poll_interval)

    return poll_for_model_job_to_finish


@fixture
def assert_text_in_resp(resp_text):

    def text_in_resp(text, resp, errors_list, add_text=''):

        actual_resp = resp_text(resp)
        if text not in resp_text(resp):
            errors_list.append(ERROR_TEXT_NOT_IN_RESP.format(text, add_text, actual_resp))

    return text_in_resp


@fixture
def assert_not_text_in_resp(resp_text):

    def text_not_in_resp(text, resp, errors_list, add_text=''):

        actual_resp = resp_text(resp)
        if text in resp_text(resp):
            errors_list.append(ERROR_TEXT_IN_RESP.format(text, add_text, actual_resp))

    return text_not_in_resp


@fixture
def assert_status_code(status_code):

    def status_code_(resp, expected_code, errors_list):

        actual_status_code = status_code(resp)
        if actual_status_code != expected_code:
            errors_list.append(
                STATUS_ERROR_TEXT.format(expected_code, actual_status_code))

    return status_code_


@fixture
def assert_json_resp(resp_json):

    def json_resp_(resp, expected_resp, errors_list, add_text=''):

        actual_resp = resp_json(resp)
        if actual_resp != expected_resp:
            errors_list.append(
                ERROR_JSON_RESP.format(add_text, expected_resp, actual_resp))

    return json_resp_


@fixture
def assert_key_in_resp(get_value_from_json_response):

    def key_in_resp(resp, key, expected_value, errors_list):

        actual_value = get_value_from_json_response(resp, key)
        if actual_value != expected_value:
            errors_list.append(
                ERROR_JSON_KEY.format(expected_value, key, actual_value))

    return key_in_resp


@fixture
def assert_is_valid_iso_date():

    def is_valid_iso_date(date_str, errors_list):

        if not is_iso_date_valid(date_str):
            errors_list.append(f'{date_str} is not a valid iso date')

    return is_valid_iso_date


@fixture
def assert_current_utc_time_in_date():
    """
    Assert that current date and time in iso format (e.g. 2020-09-22T14)
    is present in date string.
    """
    def date_is_today(date_str, errors_list, timespec='hours'):

        # timespec: hours, minutes, seconds, milliseconds
        # e.g. for minutes 2020-09-22T14:47 in 2020-09-22T07:29:49.318428+00:00
        current_date_time = str(datetime.utcnow().isoformat(timespec=timespec))
        if current_date_time not in date_str:
            errors_list.append(f'{current_date_time} is not in {date_str}')

    return date_is_today


@fixture
def assert_limited_access():
    """
    Asserts that AssertionError contains:
    LIMITED_ACCESS_RESP_CODE, LIMITED_ACCESS_ERROR_CODE, LIMITED_ACCESS_MESSAGE
    """
    def limited_access(error):

        assertion_text = str(error.value)
        assert all(string in assertion_text for string in (
                LIMITED_ACCESS_RESP_CODE, LIMITED_ACCESS_ERROR_CODE, LIMITED_ACCESS_MESSAGE)), \
            f'Assertion error must contain: ' \
            f'"{LIMITED_ACCESS_RESP_CODE} {LIMITED_ACCESS_ERROR_CODE} {LIMITED_ACCESS_MESSAGE}",' \
            f' but got: "{assertion_text}"'

    return limited_access


@fixture
def resp_key_by_dynamic_json_path(resp_json):
    """
    Inserts a string to a json_path string at json_path_index.
    Returns the value of response key by the given json_path.
    """
    def resp_key_(resp, config_key, new_str='0', json_path_index=6):

        json_path = insert_into_str(
            source_str=config_key, index=json_path_index, new_str=new_str
        )
        return get_value_by_json_path(resp_json(resp), json_path)

    return resp_key_


@fixture
def get_nf_index_by_event_type(get_value_from_json_response):

    def nf_index(resp, event_type):

        nf_list = get_value_from_json_response(resp, NfKeys.DATA.value)
        nf_idx = ''
        for nf in nf_list:
            if nf['eventType'] == event_type:
                nf_idx = str(nf_list.index(nf))
                LOGGER.info('Notification with eventType %s has index: %s',
                            event_type, nf_idx)
                return nf_idx
        LOGGER.error('Incorrect index %s for notification with eventType %s',
                      nf_idx, event_type)
    return nf_index


@fixture
def assert_key_value(resp_key_by_dynamic_json_path):

    def value_is_correct(
            expected_value, resp, config_key, errors_list, nf_index='0',
            json_path_index=6, error_text=''):

        actual_value = resp_key_by_dynamic_json_path(
            resp, config_key, nf_index, json_path_index
        )
        if actual_value != expected_value:
            errors_list.append(
                # Expected notification "{}" value {}: {}, but got: {}
                NF_ERROR_TEXT.format(
                    config_key, error_text, expected_value, actual_value))

    return value_is_correct


@fixture
def assert_bool_key(resp_key_by_dynamic_json_path):

    def bool_key(
            expected_value, resp, config_key, errors_list, nf_index='0',
            json_path_index=6, error_text=''):

        actual_key = resp_key_by_dynamic_json_path(
            resp, config_key, nf_index, json_path_index
        )
        if actual_key is not expected_value:
            errors_list.append(
                # Expected notification "{}" value {}: {}, but got: {}
                NF_ERROR_TEXT.format(
                    config_key, error_text, expected_value, actual_key))

    return bool_key


@fixture
def add_feature_flag(app_client):
    """Enables or disables a feature flag for a user"""

    def add_flag(flag, flag_value=True):
        app_client.v2_add_feature_flag(flag, flag_value)

    return add_flag


@fixture
def add_feature_flags(app_client):
    """
    Adds a single or multiple feature flags to user by passing feature flags dict,
    e.g. {flag1: True, flag2: False}
    """
    def add_flags(flags_dict):
        app_client.v2_add_feature_flags(flags_dict)

    return add_flags


@fixture
def grant_credits(dr_account_client):
    """Grants credits to PayAsYouGoUser"""

    def grant_credits_(amount):
        dr_account_client.admin_adjust_balance(amount)

    return grant_credits_


@fixture
def is_credit_category_found(app_client, resp_text):
    """
    Calls GET api/v2/creditsSystem/creditUsageSummary/
    until category_name string is found in response.
    """
    def poll_for_category(category_name, timeout_period=20, poll_interval=3):

        timeout = time() + 60 * timeout_period
        while True:
            categories = resp_text(
                app_client.v2_get_credit_usage_summary(
                    billing_period_start_ts=utc_to_iso(), segment_by='category'))
            LOGGER.info(
                'Polling for %s category. Time left %s',
                category_name, time_left(timeout)
            )
            if time() > timeout:
                LOGGER.error(
                    'Timed out polling for %s category after %d minutes',
                    category_name, timeout_period)
                raise TimeoutError(
                    TIMEOUT_MESSAGE.format(
                        category_name, 'category name', categories, timeout_period)
                )
            if category_name in categories:
                LOGGER.info('Category %s is found', category_name)
                return True

            sleep(poll_interval)

    return poll_for_category


@fixture
def get_dicts_diff(resp_json):
    """
    Converts Response object to actual_dict and
    expected_json_file to expected_dict.
    Optionally, ignores keys passed to 'ignore' param of diff().
    'ignore' param must be a set of keys where each key is a list element, e.g.
    ignore=(['results', 0, 'processingTimeMS'],).
    Returns a difference list of two dicts.
    """
    def get_dicts_diff(resp, expected_json_file, set_of_ignored_keys):

        actual_dict = resp_json(resp)
        expected_dict = convert_json_to_dict(expected_json_file)

        result = diff(
            actual_dict, expected_dict, ignore=set_of_ignored_keys
        )
        return list(result)

    return get_dicts_diff
