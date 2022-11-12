import logging
from time import sleep

from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ASSERT_ERRORS,
    ANIMALS_DATASET,
    ANIMALS_TARGET,
    WHAT_IF_APP_ID,
    ERROR_JSON_KEY,
    ERROR_TEXT_NOT_IN_RESP,
    TIMEOUT_MESSAGE
)
from utils.data_enums import (
    AiAppUptimeKeys,
    MeteringType,
    ModelingMode
)
from utils.helper_funcs import (
    time,
    time_left
)


LOGGER = logging.getLogger(__name__)


@fixture
def what_if_app(grant_credits,
                setup_project,
                app_client,
                deploy_automodel,
                get_today_start_and_end_iso_ts):
    """Creates and then deletes What If Ai App"""

    grant_credits(20000)

    start_ts, end_ts = get_today_start_and_end_iso_ts()
    project_id = setup_project(ANIMALS_DATASET, ANIMALS_TARGET)

    app_client.v2_start_autopilot(
        project_id, ANIMALS_TARGET, ModelingMode.QUICK.value
    )
    app_client.poll_for_eda_done(project_id, 16)

    deployment_id = deploy_automodel(
        'Label',  project_id, 'Description'
    )
    app_id = app_client.v2_create_ai_app(
        'What If App', deployment_id, poll_interval=2
    )
    yield start_ts, end_ts, project_id, deployment_id, app_id

    app_client.v2_delete_ai_app(app_id)


@mark.credits_system
@mark.trial
def test_ai_app_metering(payg_drap_user_setup_teardown,
                         what_if_app,
                         get_ai_app_uptime_info,
                         is_credit_category_found,
                         category_credit_usage):

    ai_apps_category = 'AI Apps'
    expected_usage = 1
    expected_uptime = 3600  # seconds

    app_client, user_id = payg_drap_user_setup_teardown
    start_ts, end_ts, _, \
    deployment_id, app_id = what_if_app

    actual_app_type_id, actual_uptime, \
    actual_project_id, actual_user_id, \
    actual_deployment_id, \
    actual_app_id = get_ai_app_uptime_info(app_client, user_id,
                                           start_ts, end_ts)
    errors = []

    if actual_app_type_id != WHAT_IF_APP_ID:
        errors.append(
            ERROR_JSON_KEY.format(
                WHAT_IF_APP_ID, AiAppUptimeKeys.APP_TYPE_ID.value,
                actual_app_id)
        )
    if actual_uptime != expected_uptime:
        errors.append(
            ERROR_JSON_KEY.format(
                expected_uptime, AiAppUptimeKeys.UPTIME.value,
                actual_uptime)
        )
    if actual_project_id is not None:
        errors.append(
            ERROR_JSON_KEY.format(
                None, AiAppUptimeKeys.PID.value, actual_project_id)
        )
    if actual_user_id != user_id:
        errors.append(
            ERROR_JSON_KEY.format(
                user_id, AiAppUptimeKeys.USER_ID.value,
                actual_user_id)
        )
    if actual_deployment_id != deployment_id:
        errors.append(
            ERROR_JSON_KEY.format(
                deployment_id, AiAppUptimeKeys.DEPLOYMENT_ID.value,
                actual_deployment_id)
        )
    if actual_app_id != app_id:
        errors.append(
            ERROR_JSON_KEY.format(
                deployment_id, AiAppUptimeKeys.APP_ID.value,
                actual_app_id))

    # AI Apps category should be present in
    # GET api/v2/creditsSystem/creditUsageSummary/
    if not is_credit_category_found(ai_apps_category):
        errors.append(
            ERROR_TEXT_NOT_IN_RESP.format(ai_apps_category, ''))

    actual_usage = category_credit_usage(ai_apps_category)
    # creditUsage value returned in
    # GET api/v2/creditsSystem/creditUsageSummary/ must be 1
    if actual_usage != expected_usage:
        errors.append(
            ERROR_JSON_KEY.format(
                expected_usage, 'creditUsage', actual_usage))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def get_ai_app_uptime_info(get_value_from_json_response, resp_text):
    """
    Returns app_type_id, uptime, project_id, user_id, deployment_id, app_id values
    from GET api/v2/admin/metering/aiappUptime/activity/ response
    """
    def ai_app_uptime_info(app_client, user_id, start_ts, end_ts,
                           timeout_period=15, poll_interval=5):

        data_list = 'data'
        timeout = time() + 60 * timeout_period
        while True:
            resp = (
                app_client.v2_get_metering_activity_uptime(
                    MeteringType.AI_APP.value, user_id, start_ts, end_ts)
            )
            LOGGER.info(
                'Polling for aiappUptime. Time left %s', time_left(timeout)
            )
            if time() > timeout:
                LOGGER.error(
                    'Timed out polling for aiappUptime after %d minutes',
                    timeout_period
                )
                raise TimeoutError(
                    TIMEOUT_MESSAGE.format(
                        data_list, 'not to be empty', resp_text(resp),
                        timeout_period)
                )
            if get_value_from_json_response(resp, data_list):
                app_type_id = get_value_from_json_response(
                    resp, AiAppUptimeKeys.APP_TYPE_ID.value
                )
                uptime = get_value_from_json_response(
                    resp, AiAppUptimeKeys.UPTIME.value
                )
                project_id = get_value_from_json_response(
                    resp, AiAppUptimeKeys.PID.value
                )
                user_id = get_value_from_json_response(
                    resp, AiAppUptimeKeys.USER_ID.value
                )
                deployment_id = get_value_from_json_response(
                    resp, AiAppUptimeKeys.DEPLOYMENT_ID.value
                )
                app_id = get_value_from_json_response(
                    resp, AiAppUptimeKeys.APP_ID.value
                )
                LOGGER.info(
                    'aiappUptime info found: %s ', resp_text(resp)
                )
                return app_type_id, uptime, project_id, user_id, \
                       deployment_id, app_id

            sleep(poll_interval)

    return ai_app_uptime_info
