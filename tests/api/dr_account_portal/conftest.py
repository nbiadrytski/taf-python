import logging
from os import environ

from pytest import fixture

from utils.constants import (
    PROD_DRAP_ADMIN_USER,
    ID_24_CHARS,
    METERING_START_TS_NO_TZ,
    METERING_END_TS_NO_TZ,
    STAGING_SELF_SERVICE_TEST_USER,
    USER_PASSWORD
)
from utils.clients import Auth0Client
from utils.helper_funcs import (
    register_tests,
    account_tests,
    profile_tests,
    roles_tests,
    register_metering_data_tests,
    credit_usage_details_tests,
    adjust_balance_tests,
    adjust_balance_summary_tests
)
from utils.data_enums import (
    CreditsSystemDataSource,
    MeteringType,
    Envs,
    EnvVars
)


LOGGER = logging.getLogger(__name__)


@fixture
def users_dict():
    return {**register_tests(),
            **account_tests(),
            **profile_tests(),
            **roles_tests(),
            **register_metering_data_tests(),
            **credit_usage_details_tests(),
            **adjust_balance_tests(),
            **adjust_balance_summary_tests()}


@fixture
def admin_portal_id(auth0_client, env_params):
    if Envs.DR_ACCOUNT_STAGING.value == env_params[1]:
        return auth0_client.get_auth0_portal_id_by_username(
            STAGING_SELF_SERVICE_TEST_USER
        )
    return auth0_client.get_auth0_portal_id_by_username(
        PROD_DRAP_ADMIN_USER)


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
    app_client : AppClient
        App client object
    """
    return Auth0Client(env_params, session)


@fixture
def user_setup_and_teardown(identity,
                            app_client,
                            dr_account_client,
                            auth0_client):

    # Create PayAsYouGoUser with Auth0 account
    username, first_name, last_name = identity
    user_id = app_client.setup_self_service_user(
        username,
        first_name,
        last_name,
        # need auth0 user for DR Account Portal
        link_dr_account=True
    )
    # Register DRAP user
    resp = dr_account_client.register_user(
        username, first_name, last_name)

    # yield PayAsYouGoUser user_id
    # and PayAsYouGoUser/DRAP username, DRAP user register resp
    yield user_id, username, resp

    # Delete PayAsYouGoUser, DRAP and Auth0 users
    app_client.v2_delete_payg_user(user_id)
    dr_account_client.delete_user(dr_account_client.portal_id)
    auth0_client.delete_auth0_user(username)


@fixture
def payg_setup_teardown(identity, app_client):
    """
    Performs PayAsYouGoUser set up and tear down.
    1. Creates PayAsYouGoUser
    2. PayAsYouGoUser opens invite link to sign up
    3. PayAsYouGoUser signs up
    4. PayAsYouGoUser's API key is created
    5. Yields PayAsYouGoUser user_id
    6. Deletes PayAsYouGoUser

    Parameters
    ----------
    app_client : function
        Returns AppClient object
    identity : function
        Returns PayAsYouGoUser username, first_name and last_name
    """
    username, first_name, last_name = identity
    # Create PayAsYouGoUser
    user_id = app_client.setup_self_service_user(
        username,
        first_name,
        last_name
    )
    yield user_id

    # Delete PayAsYouGoUser
    app_client.v2_delete_payg_user(user_id)


@fixture
def new_user_auth0_token(user_setup_and_teardown,
                         dr_account_client,
                         env_params):
    """
    Creates Auth0 token for a new PayAsYouGoUser and DRAP user with Auth0 account
    and assigns it to DrAccountPortalClient auth0_auth_token attribute.
    Returns PayAsYouGoUser/DRAP username and PayAsYouGoUser user_id.

    Parameters
    ----------
    user_setup_and_teardown : function
        Returns PayAsYouGoUser user_id, username and DRAP user register resp
    dr_account_client : function
        Returns DrAccountPortalClient object
    env_params : function
        Returns app host, DRAP host, Auth host tuple

    Returns
    -------
    username, user_id : tuple
        PayAsYouGoUser/DRAP username and PayAsYouGoUser user_id
    """
    user_id, username, _ = user_setup_and_teardown

    if Envs.DR_ACCOUNT_STAGING.value == env_params[1]:
        dr_account_client.create_user_auth0_token_staging(
            username=username,
            auth0_client_id=environ[EnvVars.AUTH0_CLIENT_ID.value],
            auth0_client_secret=environ[EnvVars.AUTH0_CLIENT_SECRET.value]
        )
    else:
        dr_account_client.create_user_auth0_token_prod(
            username=username,
            password=USER_PASSWORD,
            auth0_client_id=environ[EnvVars.AUTH0_CLIENT_ID_PROD.value],
            auth0_client_secret=environ[EnvVars.AUTH0_CLIENT_SECRET_PROD.value]
        )
    return username, user_id


@fixture
def auth0_token(dr_account_client, get_user_identity, env_params):
    """
    Creates Auth0 token for a hardcoded DR Account Portal user
    and assigns it to DrAccountPortalClient auth0_auth_token attribute.
    Hardcoded users are stored in users_dict fixture.

    Parameters
    ----------
    dr_account_client : function
        Returns DrAccountPortalClient object
    get_user_identity : function
        Returns auth0 hardcoded user identity
    """
    if Envs.DR_ACCOUNT_STAGING.value == env_params[1]:
        dr_account_client.create_user_auth0_token_staging(
            username=get_user_identity[0],
            auth0_client_id=environ[AUTH0_CLIENT_ID_ENV_VAR],
            auth0_client_secret=environ[AUTH0_CLIENT_SECRET_ENV_VAR]
        )
    else:
        dr_account_client.create_user_auth0_token_prod(
            username=get_user_identity[0],
            password=environ[DRAP_ADMIN_PASSWORD_PROD],
            auth0_client_id=environ[AUTH0_CLIENT_ID_ENV_VAR_PROD],
            auth0_client_secret=environ[AUTH0_CLIENT_SECRET_ENV_VAR_PROD])


@fixture
def get_user_identity(request, users_dict):
    """
    Returns auth0 hardcoded user identity.
    Each test has a dedicated auth0 user.
    """
    test_name = request.node.name

    username = users_dict[test_name]['username']
    first_name = users_dict[test_name]['first_name']
    last_name = users_dict[test_name]['last_name']

    return username, first_name, last_name


@fixture
def portal_user_setup_teardown(dr_account_client, auth0_client, status_code,
                               get_user_identity, get_value_from_json_response):
    """Creates and deletes DataRobot Account Portal user at the end of the test"""

    username, first_name, last_name = get_user_identity
    payload = {'email': username,
               'firstName': first_name,
               'lastName': last_name}
    resp = dr_account_client.admin_register(payload, set_portal_id=True)

    # if for some reason a user is already registered and non-200 status code is returned
    # then get portalId from user auth0 app_metadata, delete the user and register again
    if status_code(resp) != 200:
        portal_id = auth0_client.get_auth0_portal_id_by_username(username)
        try:
            dr_account_client.delete_user(portal_id)
        except AssertionError as e:
            LOGGER.warning(e)
        dr_account_client.register_user(username, first_name, last_name)

    yield

    dr_account_client.delete_user(dr_account_client.portal_id)


@fixture
def portal_user_setup(dr_account_client, auth0_client, status_code,
                      get_user_identity, get_value_from_json_response):
    """Creates DataRobot Account Portal user"""

    username, first_name, last_name = get_user_identity
    payload = {'email': username,
               'firstName': first_name,
               'lastName': last_name}
    resp = dr_account_client.admin_register(payload, set_portal_id=True)

    # if for some reason a user is already registered and non-200 status code is returned
    # then get portalId from user auth0 app_metadata, delete the user and register again
    if status_code(resp) != 200:
        portal_id = auth0_client.get_auth0_portal_id_by_username(username)
        dr_account_client.delete_user(portal_id)

        dr_account_client.register_user(username, first_name, last_name)


@fixture
def portal_user_teardown(dr_account_client):
    yield
    dr_account_client.delete_user(dr_account_client.portal_id)


@fixture
def give_initial_credits(dr_account_client):
    dr_account_client.admin_adjust_balance(value=20000, reason='initial credits')


@fixture
def default_account_resp():
    def resp(username):
        return {'email': username,
                'language': None,
                'multiFactorAuth':
                    {'otp': {'enabled': None}}}
    return resp


@fixture
def account_resp():
    def resp(username, lang=None, otp=None):
        return {'email': username,
                'language': lang,
                'multiFactorAuth':
                    {'otp': {'enabled': otp}}}
    return resp


@fixture
def register_single_user_data(dr_account_client, metering_data):
    def single_user_data(value=1.5, start=METERING_START_TS_NO_TZ, end=METERING_END_TS_NO_TZ):
        payload = metering_data(value, start, end)
        dr_account_client.admin_register_metering_data(payload, check_status_code=False)
    return single_user_data


@fixture
def metering_data_with_payg(payg_setup_teardown, get_user_identity):
    return {'billingPeriodStartTs': METERING_START_TS_NO_TZ,
            'billingPeriodEndTs': METERING_END_TS_NO_TZ,
            'activeUsers': [{'email': get_user_identity[0],
                             'uid': payg_setup_teardown,
                             'operations': [
                                 {'operationDetails':
                                      {'category': 'Some category'},
                                  'source': CreditsSystemDataSource.METERING.value,
                                  'value': 1.5}]}]}


@fixture
def metering_data(new_user_auth0_token):
    username, user_id = new_user_auth0_token

    def data(value,
             start=METERING_START_TS_NO_TZ,
             end=METERING_END_TS_NO_TZ,
             single_user=True):

        metering_deploy_uptime = {'projectName': '10k_diabetes_糖尿病',
                                  'deploymentLabel': 'label_ラベル',
                                  'type': 'shared_共有した',
                                  'category': 'ML 開発',
                                  'workerSize': 'large_大',
                                  'executionTimeMilliseconds': 12345,
                                  'uptimeSeconds': 54321}

        metering_overage_mmjob = {'projectName': 'banking кредит',
                                  'type': 'single одиночный',
                                  'category': 'MM служба',
                                  'workerSize': 'small маленький',
                                  'uptimeSeconds': 0000000}

        user = {'email': username,
                'uid': user_id,
                'operations': [
                    {'projectId': ID_24_CHARS,
                     'deploymentId': ID_24_CHARS,
                     'operationDetails': metering_deploy_uptime,
                     'source': CreditsSystemDataSource.METERING.value,
                     'metricType': MeteringType.DEPLOYMENT.value,
                     'value': value},
                    {'projectId': ID_24_CHARS,
                     'operationDetails': metering_overage_mmjob,
                     'source': CreditsSystemDataSource.METERING_OVERAGE.value,
                     'metricType': MeteringType.MMJOB.value,
                     'value': value + 1.9},
                    {'projectId': ID_24_CHARS,
                     'deploymentId': ID_24_CHARS,
                     'operationDetails': {'category': 'Predictions'},
                     'source': CreditsSystemDataSource.MANUAL_UPDATE.value,
                     'metricType': MeteringType.PREDICTIONS.value,
                     'value': value + 1.99},
                    {'projectId': ID_24_CHARS,
                     'operationDetails': {'category': 'Purchase категория'},
                     'source': CreditsSystemDataSource.PURCHASE.value,
                     'value': value + 1.999}]}
        if not single_user:
            return {'billingPeriodStartTs': start,
                    'billingPeriodEndTs': end,
                    'activeUsers': [user, user]}
        return {'billingPeriodStartTs': start,
                'billingPeriodEndTs': end,
                'activeUsers': [user]}
    return data


@fixture
def default_register_resp(get_user_identity):
    _, first_name, last_name = get_user_identity

    return {'company': None,
            'country': None,
            'firstName': first_name,
            'industry': None,
            'lastName': last_name,
            'learningTrack': None,
            'phoneNumber': None,
            'role': None,
            'socialProfiles':
                {'github': None,
                 'kaggle': None,
                 'linkedin': None},
            'state': None}


@fixture
def profile_fields_over_limits():
    def profile_fields(portal_id, profile_route=True):
        chars_256 = 256 * 'e'
        url_256_chars = 'https://test.com' + 240 * 'c'

        body = {'portalId': portal_id,
                'firstName': chars_256,
                'lastName': chars_256,
                'phoneNumber': 21 * '1',
                'language': 11 * 'c',
                'company': chars_256,
                'learningTrack': 'Paxata',
                'role': 'User',
                'socialProfiles': {'linkedin': url_256_chars,
                                   'kaggle': url_256_chars,
                                   'github': url_256_chars},
                'industry': chars_256,
                'country': 'USA',
                'state': 'TXS'}

        if profile_route:
            return body

        del body['portalId']
        body.update({'email': chars_256})
        return body

    return profile_fields


@fixture
def fields_limits():
    return {'errors':
                {'email': 'String is longer than 254 characters',
                 'language': 'String is longer than 10 characters',
                 'firstName': 'String is longer than 255 characters',
                 'lastName': 'String is longer than 255 characters',
                 'phoneNumber': 'String is longer than 20 characters',
                 'company': 'String is longer than 255 characters',
                 'industry': 'value is not a valid industry',
                 'role': 'value is not a valid role',
                 'learningTrack': 'value is not a valid learning track',
                 'country': 'String is longer than 2 characters',
                 'state': 'String is longer than 2 characters',
                 'socialProfiles__linkedin': 'String is longer than 255 characters',
                 'socialProfiles__kaggle': 'String is longer than 255 characters',
                 'socialProfiles__github': 'String is longer than 255 characters'}}


@fixture
def success_register_resp(dr_account_client):
    def register_resp(dr_account_updated=False):
        return {'portalId': dr_account_client.portal_id,
                'dr_account_updated': dr_account_updated}
    return register_resp


@fixture
def ml_category():
    def ml_category_(value=1.5):
        return {'projectId': '12345678901234567890abcd',
                'projectName': '10k_diabetes_糖尿病',
                'deploymentId': '12345678901234567890abcd',
                'deploymentLabel': 'label_ラベル',
                'category': 'ML 開発',
                'creditUsage': value}  # 1.5
    return ml_category_


@fixture
def prediction_category():
    def prediction_category_(value=3.49):
        return {'projectId': '12345678901234567890abcd',
                'projectName': None,
                'deploymentId': '12345678901234567890abcd',
                'deploymentLabel': None,
                'category': 'Predictions',
                'creditUsage': value}
    return prediction_category_


@fixture
def mm_category():
    def mm_category_(value=3.4):
        return {'projectId': '12345678901234567890abcd',
                'projectName': 'banking кредит',
                'deploymentId': None,
                'deploymentLabel': None,
                'category': 'MM служба',
                'creditUsage': value}
    return mm_category_


@fixture
def purchase_category():
    def purchase_category_(value=3.499):
        return {'category': 'Purchase категория',
                'creditUsage': value,
                'deploymentId': None,
                'deploymentLabel': None,
                'projectId': '12345678901234567890abcd',
                'projectName': None}
    return purchase_category_
