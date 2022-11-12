from time import time
import logging

from time import sleep
from pytest import (
    raises,
    fixture,
    mark
)

from utils.constants import (
    TEN_K_DIABETES_DATASET,
    STATUS_CODE,
    TEN_K_DIABETES_PREDICTION_DATASET,
    TEN_K_DIABETES_TARGET,
    ARIMA_TIME_SERIES_DATASET,
    ARIMA_TIME_SERIES_TARGET,
    REGRESSION_HEALTH_EXPEND_DATASET,
    REGRESSION_HEALTH_EXPEND_PREDICTION_DATASET,
    REGRESSION_HEALTH_EXPEND_TARGET,
    API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
    ASSERT_ERRORS
)
from utils.helper_funcs import time_left
from utils.errors import DeployedModelNotReplacedException
from utils.data_enums import (
    DeploymentsKeys,
    ServiceStatsKeys,
    ModelingMode,
    Envs
)


LOGGER = logging.getLogger(__name__)

# constants used across the tests
DESCRIPTION = 'Automodel description: 你好 Straße شارع юркий шмель'
LABEL = 'Automodel label: 你好 Straße شارع юркий шмель'

TEN_K_DIABETES_PREDICTION_ROWS = 50

TIME_SERIES_AUTOMODEL_TITLE = 'Recommended model for y (actual) on arima1_train.csv'
REGRESSION_HEALTH_EXPEND_PREDICTION_ROWS = 271
DATETIME_PARTITION_COLUMN = 'date'

CREATED, DEPLOYED, REPLACED = 'created', 'deployed', 'model replaced'
HAS_AUTOMODEL = 'hasAutomodel'
HISTORY = 'modelHistory'


@fixture
def model_data_action(resp_json):

    def model_data_action_(action_log, data_index):
        return resp_json(action_log)['data'][data_index]['action']

    return model_data_action_


@fixture
def deployment_history_has_automodel(resp_json):

    def history_has_automodel(deployment_history, model_history_index, has_automodel=True):
        if has_automodel:
            return resp_json(deployment_history)[HISTORY][model_history_index][HAS_AUTOMODEL]
        return HAS_AUTOMODEL in resp_json(deployment_history)[HISTORY][model_history_index]

    return history_has_automodel


@fixture
def replacement_reason(resp_json):

    def replacement_reason_(deployment_history, model_history_index):
        return resp_json(deployment_history)[HISTORY][model_history_index]['reason']

    return replacement_reason_


@mark.trial
@mark.automodels
def test_replace_automodel_manually(
        app_client, user_setup_and_teardown, setup_project, teardown_project,
        make_single_predictions, deploy_automodel, is_model_replaced, resp_json,
        model_data_action, deployment_history_has_automodel, replacement_reason,
        env_params):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)

    # wait until post-Start EDA is done
    app_client.poll_for_eda_done(project_id, 17, poll_interval=1)

    # deploy Automodel
    deployment_id = deploy_automodel(LABEL, project_id, DESCRIPTION)

    # wait until Automodel is auto-replaced
    if not is_model_replaced(deployment_id, timeout_period=30):
        raise DeployedModelNotReplacedException(app_client, deployment_id, 1)

    # get model id of the model which was initially deployed
    # to ensure it's ready and valid to replace auto-replaced Automodel
    replacement_model_id = resp_json(
        app_client.v2_deployment_info(deployment_id))[HISTORY][-1]['modelId']

    # manually replace Automodel with initially deployed model
    app_client.v2_replace_deployment_model(deployment_id,
                                           replacement_model_id,
                                           reason='OTHER')

    # Automodel replacement data: created, deployed, model replaced
    action_log = app_client.v2_deployments_action_log(deployment_id)
    # Deployment history: modelType, replacement reason, hasAutomodel
    deployment_history = app_client.v2_deployment_info(deployment_id)

    predictions = None
    if Envs.STAGING.value in env_params[0]:
        # make predictions with manually replaced Automodel
        predictions = make_single_predictions(deployment_id,
                                              TEN_K_DIABETES_PREDICTION_DATASET,
                                              TEN_K_DIABETES_PREDICTION_ROWS)

    app_client.v2_delete_deployment(deployment_id)

    # Automodel created
    assert model_data_action(action_log, 0) == CREATED, \
        f'There is no `action`: `{CREATED}` at [data][0] --> {action_log}'

    # deployed Automodel has hasAutomodel: true
    assert model_data_action(action_log, 1) == DEPLOYED, \
        f'There is no `action`: `{DEPLOYED}` at [data][1] --> {action_log}'

    assert deployment_history_has_automodel(deployment_history, 1), \
        f'Deployed Automodel has `{HAS_AUTOMODEL}`: false or ' \
        f'`{HAS_AUTOMODEL}` key is absent at [modelHistory][1] --> {deployment_history}'

    # auto-replaced Automodel has hasAutomodel: true
    # and was manually replaced with reason Other
    assert model_data_action(action_log, 2) == REPLACED, \
        f'There is no `action`: `{REPLACED}` at [data][2] --> {action_log}'

    assert deployment_history_has_automodel(deployment_history, 2), \
        f'Auto-replaced Automodel has `{HAS_AUTOMODEL}`: false or ' \
        f'`{HAS_AUTOMODEL}` key is absent at [modelHistory][2] --> {deployment_history}'

    assert replacement_reason(deployment_history, 1) == 'Other', \
        f'Incorrect Automodel replacement reason ' \
        f'at [modelHistory][1] --> {deployment_history}'

    # manually replaced Automodel doesn't have hasAutomodel key,
    assert model_data_action(action_log, 3) == REPLACED, \
        f'There is no `action`: `{REPLACED}` at [data][3] --> {action_log}'

    assert not deployment_history_has_automodel(
        deployment_history, 0, has_automodel=False), \
        f'`{HAS_AUTOMODEL}` key is present for manually replaced Automodel ' \
        f'at [modelHistory][0] --> {deployment_history}'

    # replacement reason is null
    assert replacement_reason(deployment_history, 0) is None, \
        f'Replacement reason at [modelHistory][0] is not null ' \
        f'for manually replaced Automodel --> {deployment_history}'

    initially_deployed_model_id = resp_json(deployment_history)[HISTORY][2]['modelId']
    # initially deployed modelId = replacement modelId
    assert replacement_model_id == initially_deployed_model_id, \
        f'Replacement modelId {replacement_model_id} != ' \
        f'initially deployed modelId {initially_deployed_model_id}'

    actions_number = len(resp_json(action_log)['data'])
    # 4 actions happened: created, deployed, model (auto)replaced, model (manually)replaced
    assert actions_number == 4, \
        f'Unexpected number of actions: {actions_number}, should be 4: ' \
        f'{CREATED}, {DEPLOYED}, {REPLACED} (auto), {REPLACED} (manually) --> {action_log}'

    if Envs.STAGING.value in env_params[0]:
        prediction_rows = len(predictions.json()['data'])
        # 50 rows of predictions returned for manually replaced Automodel
        assert prediction_rows == 50, \
            f'Expected to get 50 predictions rows, but got: {prediction_rows} --> {predictions}'


@mark.trial
@mark.automodels
def test_timeseries_predict_against_deployed_automodel(
        app_client, user_setup_and_teardown, setup_project, teardown_project,
        deploy_automodel, get_value_from_json_response, resp_json, env_params):

    app_client.v2_add_feature_flag('ENABLE_TIME_SERIES', True)

    # create Time Series project and set 'Sales' target
    project_id = setup_project(ARIMA_TIME_SERIES_DATASET,
                               ARIMA_TIME_SERIES_TARGET)
    # analyze datetimePartitionColumn
    app_client.v2_analyze_datetime_partition_column(project_id,
                                                    DATETIME_PARTITION_COLUMN)
    # run Autopilot in quick mode
    app_client.v2_start_autopilot(project_id,
                                  ARIMA_TIME_SERIES_TARGET,
                                  ModelingMode.QUICK.value,
                                  datetime_partition_column=DATETIME_PARTITION_COLUMN,
                                  windows_basis_unit='DAY',
                                  cv_method='datetime',
                                  time_series=True)
    # wait until target is set and Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 16)

    # wait until Automodel is deployed
    deployment_id = deploy_automodel(LABEL, project_id, DESCRIPTION)

    predictions = None
    if Envs.STAGING.value in env_params[0]:
        # make predictions against Automodel deployment while Autopilot is running
        predictions = app_client.make_time_series_predictions(deployment_id,
                                                              ARIMA_TIME_SERIES_DATASET,
                                                              forecast_point='2011-05-10')

    deployment = app_client.v2_get_deployment(deployment_id)
    deployments = app_client.v2_get_deployments()

    app_client.v2_delete_deployment(deployment_id)

    # 'label' key contains 'Automodel' in
    # GET api/v2/deployments/{deployment_id} and GET api/v2/deployments/ responses
    assert LABEL in get_value_from_json_response(deployment,
                                                 DeploymentsKeys.MODEL_LABEL.value)
    assert LABEL in resp_json(deployments)['data'][0]['label']

    # 'model.hasAutomodel' key is True in
    # GET api/v2/deployments/{deployment_id} and GET api/v2/deployments/ responses
    assert get_value_from_json_response(deployment,
                                        DeploymentsKeys.HAS_AUTOMODEL.value)
    assert resp_json(deployments)['data'][0]['model']['hasAutomodel']

    if Envs.STAGING.value in env_params[0]:
        # 7 rows of predictions returned as forecasting from 2011-05-11 to 2011-05-17
        assert len(predictions.json()['data']) == 7


@mark.trial
@mark.automodels
@mark.skip_if_env('prod')
def test_cannot_predict_against_inactive_automodel_deployment(
        app_client, user_setup_and_teardown, status_code, resp_json, setup_project,
        teardown_project, deploy_automodel, make_single_predictions):

    # create Health Expend regression project and set 'EXPENDOP' target
    project_id = setup_project(REGRESSION_HEALTH_EXPEND_DATASET,
                               REGRESSION_HEALTH_EXPEND_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(project_id,
                                  REGRESSION_HEALTH_EXPEND_TARGET,
                                  ModelingMode.QUICK.value)
    # wait until target is set and Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 16)

    # wait until Automodel is deployed
    deployment_id = deploy_automodel(LABEL, project_id, DESCRIPTION)

    # make predictions against active Automodel deployment
    predictions_active_deployment = make_single_predictions(
        deployment_id,
        REGRESSION_HEALTH_EXPEND_PREDICTION_DATASET,
        REGRESSION_HEALTH_EXPEND_PREDICTION_ROWS)

    # Deactivate Automodel deployment
    app_client.v2_change_deployment_status(deployment_id, 'inactive')

    timeout = time() + 60*7
    # try to make predictions against inactive Automodel deployment
    # even if deployment has inactive status, some time should pass
    # until predictions are actually restricted
    while True:
        predictions_inactive_deployment = app_client.make_predictions(
            deployment_id, REGRESSION_HEALTH_EXPEND_PREDICTION_DATASET)

        LOGGER.info('Polling for deployment %s to become indeed inactive. '
                    'Predictions request status: %d. '
                    'Will stop polling in: %s', deployment_id,
                    status_code(predictions_inactive_deployment), time_left(timeout))

        if status_code(predictions_inactive_deployment) == 403 or time() > timeout:

            LOGGER.info('Seems deployment %s is now inactive. '
                        'Predictions request status: %d. '
                        'Will stop polling in: %s', deployment_id,
                        status_code(predictions_inactive_deployment), time_left(timeout))
            break
        sleep(2)

    app_client.v2_delete_deployment(deployment_id)

    # 271 rows of predictions returned from a 271-row prediction dataset
    assert len(
        predictions_active_deployment.json()['data']) == REGRESSION_HEALTH_EXPEND_PREDICTION_ROWS

    assert resp_json(predictions_inactive_deployment) == {'message': 'Deployment is inactive'}


@mark.trial
@mark.automodels
def test_create_app_from_automodel_deployment(app_client, user_setup_and_teardown,
                                              setup_project, teardown_project,
                                              deploy_automodel):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)
    # wait until target is set and Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 16)

    # deploy Automodel
    deployment_id = deploy_automodel(LABEL, project_id, DESCRIPTION)

    app_id = app_client.v2_create_ai_app('What If App from Automodel deployment',
                                         deployment_id=deployment_id,
                                         poll_interval=2)
    app_client.v2_delete_ai_app(app_id)
    app_client.v2_delete_deployment(deployment_id)

    assert len(app_id) == 24


@mark.trial
@mark.automodels
def test_cannot_deploy_automodel_until_autopilot_starts(app_client, user_setup_and_teardown,
                                                        setup_project, teardown_project):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # try to deploy Automodel until Autopilot was started
    with raises(AssertionError) as error:
        app_client.v2_deploy_automodel(LABEL, project_id, DESCRIPTION)

    assert STATUS_CODE.format(409) and \
           'Autopilot wasn\'t started yet. ' \
           'Choose target and start Autopilot before deploying recommended model' \
           in str(error.value)


@mark.trial
@mark.automodels
def test_automodel_non_existing_project(app_client, user_setup_and_teardown):

    with raises(AssertionError) as error:
        app_client.v2_deploy_automodel(description=DESCRIPTION,
                                       label=LABEL,
                                       # valid, but non-existing project
                                       project_id='5ed4067643ed1d00f6e60000')
    assert STATUS_CODE.format(422) and \
           '{"message": "Invalid project id."}' in str(error.value)


@mark.trial
@mark.automodels
def test_automodel_no_project_id(app_client, user_setup_and_teardown,
                                 status_code, resp_json):

    payload = {'description': DESCRIPTION,
               'label': LABEL}

    resp = app_client.v2_api_post_request(
        API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
        payload,
        check_status_code=False)

    assert status_code(resp) == 422
    assert resp_json(resp) == {'message': 'Invalid field data',
                               'errors': {'projectId': 'is required'}}


@mark.trial
@mark.automodels
def test_automodel_non_existing_prediction_server(app_client, user_setup_and_teardown,
                                                  teardown_project, status_code, assert_json_resp,
                                                  env_params, resp_json, assert_status_code):

    # valid, but non-existing defaultPredictionServerId
    payload = {'defaultPredictionServerId': '5e8c41e523d66b002480e000',
               'projectId': app_client.create_project_without_dataset(),
               'description': DESCRIPTION,
               'label': LABEL}

    resp = app_client.v2_api_post_request(
        API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
        payload,
        check_status_code=False)

    errors = []

    assert_status_code(resp, expected_code=422, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'message': 'Invalid field data',
                       'errors':
                           {'defaultPredictionServerId':
                                'Specifying default prediction server ID '
                                'is not supported in current DataRobot installation.'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.automodels
# valid for staging only
# defaultPredictionServerId is not required for app2 env
@mark.skip_if_env('prod')
def test_automodel_no_prediction_server(app_client, user_setup_and_teardown, status_code,
                                        resp_json, teardown_project):

    payload = {'projectId': app_client.create_project_without_dataset(),
               'description': DESCRIPTION,
               'label': LABEL}

    resp = app_client.v2_api_post_request(
        API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
        payload,
        check_status_code=False)

    assert status_code(resp) == 422
    assert resp_json(resp) == {'errors': {'defaultPredictionServerId':
                                              'Specifying default prediction server ID '
                                              'is required in DataRobot Cloud.'},
                               'message': 'Invalid field data'}


@mark.trial
@mark.automodels
def test_automodel_no_label_and_description(app_client, user_setup_and_teardown,
                                            status_code, resp_json, teardown_project):

    payload = {'projectId': app_client.create_project_without_dataset()}

    resp = app_client.v2_api_post_request(
        API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
        payload,
        check_status_code=False)

    assert status_code(resp) == 422
    assert resp_json(resp) == {'message': 'Invalid field data',
                               'errors': {'label': 'is required'}}


@mark.trial
@mark.automodels
def test_deploy_automodel_three_times(app_client, user_setup_and_teardown,
                                      setup_project, teardown_project):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)
    # wait until target is set and Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 17)

    # start Automodel deployment: 1
    automodel_id_1st_request = app_client.v2_deploy_automodel(LABEL,
                                                              project_id,
                                                              DESCRIPTION)
    payload = {'projectId': project_id,
               'label': LABEL,
               'description': DESCRIPTION}

    # start Automodel deployment: 2
    automodel_2nd_request = app_client.v2_api_post_request(
        API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH, payload)

    # wait until Automodel is deployed
    deployment_id = app_client.v2_poll_for_first_available_deployment()

    # start Automodel deployment: 3
    automodel_3rd_request = app_client.v2_api_post_request(
        API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH, payload)

    app_client.v2_delete_deployment(deployment_id)

    # just one Automodel per project
    assert automodel_id_1st_request == \
           automodel_2nd_request.json()['id'] == automodel_3rd_request.json()['id']


@mark.trial
@mark.automodels
@mark.skip_if_env('prod')
def test_automodel_cannot_predict_with_explanations(app_client, user_setup_and_teardown,
                                                    setup_project, deploy_automodel,
                                                    resp_json, teardown_project):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)
    # wait until target is set so that Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 16, poll_interval=1)

    # deploy Automodel
    deployment_id = deploy_automodel(LABEL, project_id, DESCRIPTION)

    # try to make single predictions with explanations against Automodel deployment
    predict_with_explanations = app_client.make_predictions_with_explanations(
        deployment_id,
        TEN_K_DIABETES_PREDICTION_DATASET)

    app_client.v2_delete_deployment(deployment_id)

    expected_resp = {'message': 'Prediction Explanations are not initialized for the model'}

    # cannot make predictions with explanations against Automodel deployment
    assert resp_json(predict_with_explanations) == expected_resp, \
        f'Expected response: {expected_resp}, but got: {predict_with_explanations}'


@mark.trial
@mark.automodels
@mark.skip_if_env('prod')
def test_automodel_auto_replacement_and_predicting(app_client, user_setup_and_teardown,
                                                   setup_project, teardown_project,
                                                   get_value_from_json_response, make_single_predictions,
                                                   is_model_replaced, model_data_action, replacement_reason,
                                                   deploy_automodel, deployment_history_has_automodel):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)
    # wait until Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 17, poll_interval=1)

    # deploy Automodel
    deployment_id = deploy_automodel(LABEL, project_id, DESCRIPTION)

    # make predictions until Automodel is replaced
    predictions_until_model_replaced = make_single_predictions(
        deployment_id, TEN_K_DIABETES_PREDICTION_DATASET, TEN_K_DIABETES_PREDICTION_ROWS)

    # check if Automodel was auto-replaced
    if not is_model_replaced(deployment_id):
        raise DeployedModelNotReplacedException(app_client, deployment_id, 1)

    timeout = time() + 60*10  # 10 minutes from now
    while True:
        predictions_rows = get_value_from_json_response(
            app_client.v2_deployment_service_stats(deployment_id),
            ServiceStatsKeys.PREDICTION_ROWS.value)

        LOGGER.info('Predictions rows == 0, actual: %s', predictions_rows)

        if time() > timeout:
            raise TimeoutError(
                f'Timed out polling for predictions rows == 0 after 10 minutes. '
                f'Actual rows: {predictions_rows}')

        if predictions_rows == 0:
            LOGGER.info('Predictions data is cleared after Automodel %s has been replaced',
                        deployment_id)
            break

    # make predictions after Automodel is replaced
    predictions_after_model_replaced = make_single_predictions(
        deployment_id, TEN_K_DIABETES_PREDICTION_DATASET, TEN_K_DIABETES_PREDICTION_ROWS)

    # Automodel replacement data is stored in action_log
    action_log = app_client.v2_deployments_action_log(deployment_id)
    # Deployment history
    deployment_history = app_client.v2_deployment_info(deployment_id)

    app_client.v2_delete_deployment(deployment_id)

    assert model_data_action(action_log, 0) == CREATED, \
        f'There is no `action`: `{CREATED}` at [data][0] --> {action_log}'

    assert model_data_action(action_log, 1) == DEPLOYED, \
        f'There is no `action`: `{DEPLOYED}` at [data][1] --> {action_log}'

    assert model_data_action(action_log, 2) == REPLACED, \
        f'There is no `action`: `{REPLACED}` at [data][2] --> {action_log}'

    assert replacement_reason(deployment_history, 1) == 'Accuracy', \
        f'Incorrect Automodel replacement reason ' \
        f'at [modelHistory][1] --> {deployment_history}'

    assert deployment_history_has_automodel(deployment_history, 1), \
        f'Deployed Automodel has `{HAS_AUTOMODEL}`: false or ' \
        f'`{HAS_AUTOMODEL}` key is absent at [modelHistory][1] --> {deployment_history}'

    assert len(predictions_until_model_replaced.json()['data']) == \
           len(predictions_after_model_replaced.json()['data']) == \
           TEN_K_DIABETES_PREDICTION_ROWS, \
        f'Number of predictions rows before Automodel was replaced and after is different'


@mark.trial
@mark.automodels
def test_automodel_no_description(app_client, user_setup_and_teardown, setup_project,
                                  teardown_project):

    # create 10k_diabetes project and set 'Readmitted' target
    project_id = setup_project(TEN_K_DIABETES_DATASET,
                               TEN_K_DIABETES_TARGET)

    # run Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)
    # wait until target is set and Automodel deployment can be started
    app_client.poll_for_eda_done(project_id, 16)

    # start Automodel deployment
    automodel_id = app_client.v2_deploy_automodel(
        label=LABEL,
        project_id=project_id,
        has_description=False)

    assert len(automodel_id) == 24
