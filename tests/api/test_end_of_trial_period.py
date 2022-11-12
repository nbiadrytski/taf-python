from pytest import (
    fixture,
    mark,
    raises
)

from utils.constants import (
    TEN_K_DIABETES_DATASET,
    TEN_K_DIABETES_TARGET
)
from utils.helper_funcs import user_identity
from utils.data_enums import (
    UserType,
    ModelingMode
)


@fixture(scope='module')
def user_setup_and_teardown(app_client):
    """Creates and then deletes TrialUser after all tests are done."""
    username, first_name, last_name = user_identity()
    user_id = app_client.setup_self_service_user(
        username,
        first_name,
        last_name,
        user_type=UserType.TRIAL_USER.value)

    yield app_client, user_id

    app_client.v2_delete_payg_user(user_id)


@fixture(scope='module')
def end_of_trial_setup(user_setup_and_teardown):
    app_client, _ = user_setup_and_teardown

    project_id, bp_id, model_id, deployment_id = \
        app_client.setup_10k_diabetes_project()

    # Set user's expirationDate back to 15 days
    # so that Trial period is over for the user
    app_client.v2_update_user_expiration_date(days=15, ahead=False)

    # return app_client, project.id, bp_id, model_id, deployment_id
    yield app_client, project_id, bp_id, model_id, deployment_id

    app_client.v2_update_user_expiration_date(days=15, ahead=True)
    app_client.v2_delete_deployment(deployment_id)
    app_client.v2_delete_project_by_project_id(project_id)


@mark.trial
@mark.end_of_trial
def test_cannot_create_project_after_trial_is_over(end_of_trial_setup,
                                                   assert_limited_access):
    app_client, _, _, _, _ = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_create_project_from_file(TEN_K_DIABETES_DATASET)

    assert_limited_access(error)


@mark.trial
@mark.end_of_trial
def test_cannot_train_model_after_trial_is_over(end_of_trial_setup,
                                                assert_limited_access):
    app_client, project_id, bp_id, model_id, _ = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_train_model(project_id, bp_id)

    assert_limited_access(error)


@mark.trial
@mark.end_of_trial
def test_cannot_start_autopilot_after_trial_is_over(end_of_trial_setup,
                                                    assert_limited_access):
    app_client, project_id, _, _, _ = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_start_autopilot(
            project_id, TEN_K_DIABETES_TARGET, ModelingMode.QUICK.value)

    assert_limited_access(error)


@mark.trial
@mark.end_of_trial
def test_cannot_deploy_model_after_trial_is_over(end_of_trial_setup,
                                                 assert_limited_access):
    app_client, project_id, bp_id, model_id, _ = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_deploy_from_learning_model(model_id)

    assert_limited_access(error)


@mark.trial
@mark.end_of_trial
def test_cannot_deploy_automodel_after_trial_is_over(end_of_trial_setup,
                                                     assert_limited_access):
    app_client, project_id, bp_id, model_id, _ = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_deploy_automodel('Automodel label',
                                       project_id)
    assert_limited_access(error)


@mark.trial
@mark.end_of_trial
def test_cannot_delete_deployment_after_trial_is_over(end_of_trial_setup,
                                                      assert_limited_access):
    app_client, _, _, _, deployment_id = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_delete_deployment(deployment_id)

    assert_limited_access(error)


@mark.trial
@mark.end_of_trial
def test_cannot_delete_project_after_trial_is_over(end_of_trial_setup,
                                                   assert_limited_access):
    app_client, project_id, _, _, _ = end_of_trial_setup

    with raises(AssertionError) as error:
        app_client.v2_delete_project_by_project_id(project_id)

    assert_limited_access(error)
