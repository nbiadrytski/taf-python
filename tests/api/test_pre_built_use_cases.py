from pytest import (
    fixture,
    mark,
    raises
)

from utils.constants import (
    ASSERT_ERRORS,
    STATUS_CODE
)
from utils.data_enums import RecommendedModelsKeys
from utils.data_enums import FeatureFlags


@fixture
def demo_cases_ids(user_setup_and_teardown, app_client,
                   resp_json):
    """Returns a list of demo datasets use cases ids"""
    app_client.v2_add_feature_flag(
        FeatureFlags.ENABLE_DEMO_USE_CASE_SHARING.value)

    use_cases = resp_json(
        app_client.v2_get_demo_use_cases('demoDatasets'))

    use_cases_ids = []
    for use_case in use_cases:
        use_cases_ids.append(use_case['demoDatasetId'])

    yield use_cases_ids


@fixture
def pathfinder_cases_ids(user_setup_and_teardown,
                         app_client,
                         resp_json):

    """Returns a list of pathfinder use cases ids"""
    app_client.v2_add_feature_flag(
        FeatureFlags.ENABLE_DEMO_USE_CASE_SHARING.value
    )
    app_client.v2_add_feature_flag(
        FeatureFlags.ENABLE_USE_CASE_LIBRARY_SYNC.value
    )
    use_cases = resp_json(
        app_client.v2_get_demo_use_cases('pathfinderUseCases')
    )['data']

    use_cases_ids = []
    for use_case in use_cases:
        use_cases_ids.append(use_case['useCaseId'])

    yield use_cases_ids


@fixture
def assert_case_is_explorable(app_client, get_value_from_json_response):

    def explore_case(project_id, use_case_id):
        errors = []

        try:
            models = app_client.v2_get_recommended_models(project_id)
        except (AssertionError, IndexError) as error:
            raise Exception(
                f'Failed to get model for use case {use_case_id}. '
                f'Error: {error}')

        # Get recommended modelId
        model_id = get_value_from_json_response(
            models,
            RecommendedModelsKeys.RECOMMENDED_MODEL.value)

        try:
            # Create model package from the recommended model
            package_id = app_client.v2_create_package_from_learning_model(
                model_id, 'Recommended model')
        except AssertionError as error:
            raise Exception(
                f'Failed to create package for use case {use_case_id}. '
                f'Error: {error}')

        try:
            # Deploy model from package
            deployment_id = app_client.v2_deploy_from_model_package(package_id)
        except AssertionError as error:
            raise Exception(
                f'Failed to deploy from package for use case {use_case_id}. '
                f'Error: {error}')

        # Assert valid deploymentId returned when deploying a model
        # for the pre-built use case
        if len(deployment_id) != 24:
            errors.append(
                f'Use case {use_case_id} model was not deployed.'
                f'deploymentId: {deployment_id}')

        # Automodel cannot be deployed
        with raises(AssertionError) as error:
            app_client.v2_deploy_automodel('Automodel',
                                           project_id)
        if STATUS_CODE.format(403) not in str(error.value):
            errors.append(
                f'Seems user can deploy Automodel for pre-built use case.'
                f' Error: {error.value}')

        assert not errors, ASSERT_ERRORS.format('\n'.join(errors))

    return explore_case


@mark.prebuilt_use_cases
@mark.trial
def test_pathfinder_use_cases(pathfinder_cases_ids, app_client,
                              assert_case_is_explorable):

    for use_case in pathfinder_cases_ids:
        project_id = app_client.v2_explore_pre_built_use_case(use_case)

        assert_case_is_explorable(project_id, use_case)


@mark.prebuilt_use_cases
@mark.trial
def test_demo_use_cases(demo_cases_ids, app_client, assert_case_is_explorable):

    for use_case in demo_cases_ids:
        project_id = app_client.v2_explore_pre_built_use_case(use_case)

        assert_case_is_explorable(project_id, use_case)
