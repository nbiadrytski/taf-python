from pytest import (
    fixture,
    mark
)

from utils.constants import (
    TEN_K_DIABETES_DATASET,
    TEN_K_DIABETES_TARGET,
    TEN_K_DIABETES_PREDICTION_DATASET_URL,
    ERROR_JSON_KEY,
    ERROR_TEXT_NOT_IN_RESP,
    ASSERT_ERRORS
)
from utils.data_enums import (
    MeteringType,
    PredictionUptimeKeys,
    ModelingMode
)


@fixture
def make_predictions(payg_drap_user_setup_teardown,
                     grant_credits,
                     get_today_start_and_end_iso_ts,
                     deploy_automodel, setup_project):

    app_client, user_id = payg_drap_user_setup_teardown
    grant_credits(20000)

    start_ts, end_ts = get_today_start_and_end_iso_ts()

    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    app_client.v2_start_autopilot(
        project_id,
        TEN_K_DIABETES_TARGET,
        ModelingMode.QUICK.value
    )
    app_client.poll_for_eda_done(project_id, 16)

    deployment_id = deploy_automodel(
        'Label',
        project_id,
        'Description'
    )
    # Upload 10k_diabetes predictions dataset
    dataset_id = app_client.v2_upload_dataset_via_url(
        TEN_K_DIABETES_PREDICTION_DATASET_URL
    )
    # Make 5 batch predictions
    for i in range(5):
        app_client.v2_make_batch_predictions(
            deployment_id, dataset_id
        )
    yield app_client, user_id, start_ts, end_ts, \
          project_id, deployment_id


@mark.credits_system
@mark.trial
def test_predictions_are_metered(make_predictions,
                                 is_credit_category_found,
                                 category_credit_usage,
                                 get_prediction_exec_time_info):

    predictions_category = 'ML Predictions'
    expected_usage = 1

    app_client, user_id, start_ts, end_ts, \
    project_id, deployment_id = make_predictions

    actual_exec_time, actual_project_id, actual_user_id, \
    actual_deployment_id = get_prediction_exec_time_info(
        app_client, user_id, start_ts, end_ts
    )

    errors = []

    if actual_exec_time <= 0:
        errors.append(
            ERROR_JSON_KEY.format(
                '<= 0',
                PredictionUptimeKeys.EXEC_TIME.value,
                actual_exec_time)
        )
    if actual_project_id != project_id:
        errors.append(
            ERROR_JSON_KEY.format(
                project_id,
                PredictionUptimeKeys.PID.value,
                actual_project_id)
        )
    if actual_user_id != user_id:
        errors.append(
            ERROR_JSON_KEY.format(
                user_id,
                PredictionUptimeKeys.USER_ID.value,
                actual_user_id)
        )
    if actual_deployment_id != deployment_id:
        errors.append(
            ERROR_JSON_KEY.format(
                deployment_id,
                PredictionUptimeKeys.DEPLOYMENT_ID.value,
                actual_deployment_id)
        )

    # ML Predictions category should be present in
    # GET api/v2/creditsSystem/creditUsageSummary/ resp
    if not is_credit_category_found(predictions_category):
        errors.append(
            ERROR_TEXT_NOT_IN_RESP.format(
                predictions_category, ''))

    actual_usage = category_credit_usage(predictions_category)
    # creditUsage value returned in
    # GET api/v2/creditsSystem/creditUsageSummary/ must be 1
    if actual_usage != expected_usage:
        errors.append(
            ERROR_JSON_KEY.format(
                expected_usage, 'creditUsage', actual_usage))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def get_prediction_exec_time_info(get_value_from_json_response):
    """
    Returns exec_time, project_id, user_id, deployment_id values
    from GET api/v2/admin/metering/prediction/activity/ response
    """
    def prediction_exec_time_info(
            app_client, user_id, start_ts, end_ts
    ):
        resp = (
            app_client.v2_get_metering_activity_uptime(
                MeteringType.PREDICTIONS.value,
                user_id,
                start_ts, end_ts)
        )
        exec_time = get_value_from_json_response(
            resp, PredictionUptimeKeys.EXEC_TIME.value
        )
        project_id = get_value_from_json_response(
            resp, PredictionUptimeKeys.PID.value
        )
        user_id = get_value_from_json_response(
            resp, PredictionUptimeKeys.USER_ID.value
        )
        deployment_id = get_value_from_json_response(
            resp, PredictionUptimeKeys.DEPLOYMENT_ID.value
        )
        return exec_time, project_id, user_id, deployment_id

    return prediction_exec_time_info
