import logging
from time import sleep

from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ASSERT_ERRORS,
    ERROR_JSON_KEY,
    ERROR_TEXT_NOT_IN_RESP,
    TIMEOUT_MESSAGE
)
from utils.data_enums import (
    DeploymentUptimeKeys,
    MeteringType
)
from utils.helper_funcs import (
    time_left,
    time
)


LOGGER = logging.getLogger(__name__)


@fixture
def deployment(grant_credits, app_client,
               get_today_start_and_end_iso_ts):
    """Creates deployment"""
    grant_credits(20000)

    start_ts, end_ts = get_today_start_and_end_iso_ts()

    project_id, _, _, deployment_id = \
        app_client.setup_10k_diabetes_project()

    yield start_ts, end_ts, project_id, deployment_id


@mark.credits_system
@mark.trial
def test_deployment_metering(payg_drap_user_setup_teardown,
                             deployment,
                             poll_for_deploy_uptime,
                             get_deployment_uptime_info,
                             is_credit_category_found,
                             category_credit_usage):

    ml_ops_category = 'MLOps'
    expected_usage = 1
    expected_uptime = 3600  # seconds
    expected_deployment_type = 'shared'

    app_client, user_id = payg_drap_user_setup_teardown
    start_ts, end_ts, \
    project_id, deployment_id = deployment

    poll_for_deploy_uptime(user_id, start_ts, end_ts)

    actual_uptime, actual_project_id, \
    actual_user_id, actual_deployment_id, \
    actual_deployment_type = get_deployment_uptime_info(
        app_client, user_id, start_ts, end_ts
    )

    errors = []

    if actual_deployment_type != expected_deployment_type:
        errors.append(
            ERROR_JSON_KEY.format(
                expected_deployment_type,
                DeploymentUptimeKeys.DEPLOYMENT_TYPE.value,
                actual_deployment_type)
        )
    if actual_uptime != expected_uptime:
        errors.append(
            ERROR_JSON_KEY.format(
                expected_uptime,
                DeploymentUptimeKeys.UPTIME.value,
                actual_uptime)
        )
    if actual_project_id != project_id:
        errors.append(
            ERROR_JSON_KEY.format(
                project_id,
                DeploymentUptimeKeys.PID.value,
                actual_project_id)
        )
    if actual_user_id != user_id:
        errors.append(
            ERROR_JSON_KEY.format(
                user_id,
                DeploymentUptimeKeys.USER_ID.value,
                actual_user_id)
        )
    if actual_deployment_id != deployment_id:
        errors.append(
            ERROR_JSON_KEY.format(
                deployment_id,
                DeploymentUptimeKeys.DEPLOYMENT_ID.value,
                actual_deployment_id)
        )
    if actual_deployment_id != deployment_id:
        errors.append(
            ERROR_JSON_KEY.format(
                deployment_id,
                DeploymentUptimeKeys.DEPLOYMENT_ID.value,
                actual_deployment_id))

    # MLOps category should be present in
    # GET api/v2/creditsSystem/creditUsageSummary/
    if not is_credit_category_found(ml_ops_category):
        errors.append(
            ERROR_TEXT_NOT_IN_RESP.format(ml_ops_category, ''))

    actual_usage = category_credit_usage(ml_ops_category)
    # MLOps creditUsage value returned in
    # GET api/v2/creditsSystem/creditUsageSummary/ must be 1
    if actual_usage != expected_usage:
        errors.append(
            ERROR_JSON_KEY.format(
                expected_usage, 'creditUsage', actual_usage))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def get_deployment_uptime_info(get_value_from_json_response):
    """
    Returns uptime, project_id, user_id, deployment_id, deployment_type values
    from GET api/v2/admin/metering/deploymentUptime/activity/ response
    """
    def deployment_uptime_info(app_client, user_id, start_ts, end_ts):
        resp = (
            app_client.v2_get_metering_activity_uptime(
                MeteringType.DEPLOYMENT.value,
                user_id,
                start_ts, end_ts)
        )
        uptime = get_value_from_json_response(
            resp, DeploymentUptimeKeys.UPTIME.value
        )
        project_id = get_value_from_json_response(
            resp, DeploymentUptimeKeys.PID.value
        )
        user_id = get_value_from_json_response(
            resp, DeploymentUptimeKeys.USER_ID.value
        )
        deployment_type = get_value_from_json_response(
            resp, DeploymentUptimeKeys.DEPLOYMENT_TYPE.value
        )
        deployment_id = get_value_from_json_response(
            resp, DeploymentUptimeKeys.DEPLOYMENT_ID.value
        )
        return uptime, project_id, user_id, deployment_id, deployment_type

    return deployment_uptime_info


@fixture
def poll_for_deploy_uptime(app_client, resp_text):
    """
    Calls GET api/v2/admin/metering/deploymentUptime/activity/
    until uptimeSeconds string is found in response.
    """
    uptime_seconds = 'uptimeSeconds'

    def poll_for_deploy_uptime(
            user_id, start_ts, end_ts,
            timeout_period=10, poll_interval=1
    ):
        timeout = time() + 60 * timeout_period
        while True:
            resp = resp_text(
                app_client.v2_get_metering_activity_uptime(
                    MeteringType.DEPLOYMENT.value,
                    user_id,
                    start_ts, end_ts)
            )
            LOGGER.info(
                'Polling for user %s deployment %s. Time left %s',
                user_id, uptime_seconds, time_left(timeout)
            )
            if time() > timeout:
                LOGGER.error(
                    'Timed out polling for user %s deployment %s'
                    ' after %d minutes',
                    user_id, uptime_seconds, timeout_period
                )
                raise TimeoutError(
                    TIMEOUT_MESSAGE.format(
                        uptime_seconds,
                        'string in resp',
                        resp,
                        timeout_period
                    ))
            if uptime_seconds in resp:
                LOGGER.info(
                    'Deployment uptime for user %s is found',
                    user_id
                )
                break

            sleep(poll_interval)

    return poll_for_deploy_uptime
