from time import (
    time,
    sleep
)
import logging

from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ANIMALS_DATASET,
    ASSERT_ERRORS,
    TIMEOUT_MESSAGE,
    ERROR_JSON_KEY,
    TEN_K_DIABETES_PROJECT_NAME
)
from utils.helper_funcs import (
    user_identity,
    utc_to_iso,
    time_left
)
from utils.data_enums import CreditsCategory


LOGGER = logging.getLogger(__name__)


ANIMALS_PROJECT = 'animals.csv'
CATEGORY = 'category'
PROJECT_NAME = 'projectName'

TIMEOUT_PERIOD = 15
USAGE_SUMMARY_MSG = 'in GET creditUsageSummary/?segmentBy={}'
POLL_LOG_MSG = 'Polling for %s to be %s. Time left: %s'
FOUND_LOG_MSG = 'Found %s %s'


@fixture(scope='module')
def payg_drap_user_setup_teardown(app_client, dr_account_client):

    # Create and sign up PayAsYouGoUser
    username, first_name, last_name = user_identity()
    user_id = app_client.setup_self_service_user(username,
                                                 first_name,
                                                 last_name)
    # Register DRAP user
    dr_account_client.register_user(username, first_name, last_name)
    dr_account_client.admin_adjust_balance(200)

    yield app_client, user_id

    # Delete PayAsYouGoUser and DRAP users
    app_client.v2_delete_payg_user(user_id)
    dr_account_client.delete_user(dr_account_client.portal_id)


@fixture(scope='module')
def setup_2_projects(payg_drap_user_setup_teardown):

    app_client, _ = payg_drap_user_setup_teardown
    project_id_1, _, _, deployment_id = app_client.setup_10k_diabetes_project()
    project_id_2 = app_client.v2_create_project_from_file(ANIMALS_DATASET)

    _poll_for_categories_are_billed(app_client)
    _poll_for_projects_are_billed(app_client)

    yield app_client, project_id_1, deployment_id, project_id_2

    app_client.v2_delete_deployment(deployment_id)
    app_client.v2_delete_project_by_project_id(project_id_1)
    app_client.v2_delete_project_by_project_id(project_id_2)


@mark.credits_system
@mark.trial
def test_credit_usage_summary_by_project(setup_2_projects, assert_total_usage,
                                         resp_key_value):

    app_client, _, _, _ = setup_2_projects
    resp = app_client.v2_get_credit_usage_summary(utc_to_iso(),
                                                  segment_by=PROJECT_NAME)
    errors = []
    assert_total_usage(resp, errors)

    resp_key_value(resp,
                   expected_value=TEN_K_DIABETES_PROJECT_NAME,
                   errors_list=errors,
                   data_index=0)

    resp_key_value(resp,
                   expected_value=ANIMALS_PROJECT,
                   errors_list=errors,
                   data_index=1)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.credits_system
@mark.trial
def test_credit_usage_summary_by_category(setup_2_projects, resp_key_value,
                                          assert_total_usage):

    app_client, _, _, _ = setup_2_projects

    resp = app_client.v2_get_credit_usage_summary(utc_to_iso(),
                                                  segment_by=CATEGORY)
    errors = []
    assert_total_usage(resp, errors)

    resp_key_value(resp,
                   expected_value=CreditsCategory.DATA_PROCESSING.value,
                   errors_list=errors,
                   data_index=0)

    resp_key_value(resp,
                   expected_value=CreditsCategory.ML_DEV.value,
                   errors_list=errors,
                   data_index=1)

    resp_key_value(resp,
                   expected_value=CreditsCategory.ML_OPS.value,
                   errors_list=errors,
                   data_index=2)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def assert_total_usage(resp_json):
    """Assert credits totalUsage is >= min_value"""
    def assert_total_usage_(resp, errors_list):
        min_value = 15
        total_usage = resp_json(resp)['totalUsage']
        if not min_value <= total_usage:
            errors_list.append(
                f'Expected totalUsage >= {min_value}'
                f' got {total_usage}')
    return assert_total_usage_


@fixture
def resp_key_value(resp_json):
    """
    Assert [data][data_index][key] value
    from GET api/v2/creditsSystem/creditUsageSummary response
    """
    def resp_key_value_(resp, expected_value, errors_list, data_index=0):
        actual_value = resp_json(resp)['data'][data_index]['key']
        if actual_value != expected_value:
            errors_list.append(
                ERROR_JSON_KEY.format(
                    expected_value, '[data][index][key]', actual_value))
    return resp_key_value_


def _poll_for_projects_are_billed(app_client):

    timeout = time() + 60 * TIMEOUT_PERIOD
    while True:
        expected_text = f'{ANIMALS_PROJECT} and {TEN_K_DIABETES_PROJECT_NAME}'
        message = USAGE_SUMMARY_MSG.format(PROJECT_NAME)

        resp = app_client.v2_get_credit_usage_summary(utc_to_iso(),
                                                      segment_by=PROJECT_NAME)
        text_resp = app_client.get_response_text(resp)
        LOGGER.info(
            POLL_LOG_MSG, expected_text, message, time_left(timeout))

        if time() > timeout:
            raise TimeoutError(
                TIMEOUT_MESSAGE.format(expected_text,
                                       message,
                                       text_resp,
                                       TIMEOUT_PERIOD))

        if all(x in text_resp for x in (
                TEN_K_DIABETES_PROJECT_NAME, ANIMALS_PROJECT)
               ):
            LOGGER.info(FOUND_LOG_MSG, expected_text, message)
            break

        sleep(2)


def _poll_for_categories_are_billed(app_client):

    timeout = time() + 60 * TIMEOUT_PERIOD
    while True:
        expected_text = f'{CreditsCategory.DATA_PROCESSING.value}, ' \
                        f'{CreditsCategory.ML_DEV.value} and ' \
                        f'{CreditsCategory.ML_OPS.value}'
        message = USAGE_SUMMARY_MSG.format(CATEGORY)

        resp = app_client.v2_get_credit_usage_summary(utc_to_iso(),
                                                      segment_by=CATEGORY)
        text_resp = app_client.get_response_text(resp)
        LOGGER.info(
            POLL_LOG_MSG, expected_text, message, time_left(timeout))

        if time() > timeout:
            raise TimeoutError(
                TIMEOUT_MESSAGE.format(expected_text,
                                       message,
                                       text_resp,
                                       TIMEOUT_PERIOD))

        if all(x in text_resp for x in (
                CreditsCategory.DATA_PROCESSING.value,
                CreditsCategory.ML_DEV.value,
                CreditsCategory.ML_OPS.value)
               ):
            LOGGER.info(FOUND_LOG_MSG, expected_text, message)
            break

        sleep(2)
