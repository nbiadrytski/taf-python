import logging

from pytest import (
    fixture,
    mark,
    raises
)

from utils.helper_funcs import user_identity
from utils.constants import (
    TEN_K_DIABETES_DATASET,
    TEN_K_DIABETES_TARGET,
    TEN_K_DIABETES_XLSX_DATASET,
    ASSERT_ERRORS,
    TEN_K_DIABETES_PREDICTION_DATASET_URL,
    EUCLIDIAN_DISTANCE_MODEL
)
from utils.data_enums import (
    NfKeys,
    ModelingMode
)


LOGGER = logging.getLogger(__name__)


@fixture(scope='module')
def payg_drap_user_setup_teardown(app_client, dr_account_client):

    # Create and sign up PayAsYouGoUser
    username, first_name, last_name = user_identity()
    user_id = app_client.setup_self_service_user(username,
                                                 first_name,
                                                 last_name)
    # Register DRAP user
    dr_account_client.register_user(username, first_name, last_name)
    # Grant 8 credits to PayAsYouGoUser
    dr_account_client.admin_adjust_balance(10)

    # yield user_id, username
    yield app_client, user_id

    # Delete PayAsYouGoUser and DRAP users
    app_client.v2_delete_payg_user(user_id)
    dr_account_client.delete_user(dr_account_client.portal_id)


@fixture(scope='module')
def out_of_credits_setup(payg_drap_user_setup_teardown,
                         dr_account_client):

    app_client, _ = payg_drap_user_setup_teardown

    # 1. Create 10k_diabetes project
    project_id = app_client.v2_create_project_from_file(
        TEN_K_DIABETES_DATASET)
    app_client.set_target(TEN_K_DIABETES_TARGET, project_id)

    # 2. Start EDA in manual mode and wait until it's done
    app_client.v2_start_autopilot(project_id,
                                  TEN_K_DIABETES_TARGET,
                                  ModelingMode.MANUAL.value)
    app_client.poll_for_eda_done(project_id, 17)

    # Get blueprint id for
    # Auto-tuned K-Nearest Neighbors Classifier (Euclidean Distance) model
    bp_id = app_client.v2_get_blueprint_id(EUCLIDIAN_DISTANCE_MODEL,
                                           project_id)
    grant_a_credit_if_0(app_client, dr_account_client)
    # 3. Train a model
    model_id = app_client.v2_train_model(project_id, bp_id)

    grant_a_credit_if_0(app_client, dr_account_client)
    # 4. Deploy the model
    deployment_id = app_client.v2_deploy_from_learning_model(model_id)

    grant_a_credit_if_0(app_client, dr_account_client)
    # 5. Upload 10k_diabetes predictions dataset
    dataset_id = app_client.v2_upload_dataset_via_url(
        TEN_K_DIABETES_PREDICTION_DATASET_URL)

    # Poll for user's balance to be 0
    app_client.poll_for_balance(0)
    # Poll for Out of credits notification
    nf_resp = app_client.poll_for_notifications(1)

    yield app_client, \
          project_id, \
          bp_id, \
          model_id, \
          deployment_id, \
          dataset_id, \
          nf_resp

    # Grant credits so that user can delete deployment and project
    dr_account_client.admin_adjust_balance(100)

    app_client.v2_delete_deployment(deployment_id)
    app_client.v2_delete_project_by_project_id(project_id)


@mark.credits_system
@mark.trial
def test_read_out_of_credits_notification(out_of_credits_setup,
                                          resp_key_by_dynamic_json_path,
                                          assert_limited_access,
                                          assert_bool_key,
                                          env_params, assert_key_value):

    app_client, _, _, _, _, _, nf_resp = out_of_credits_setup

    errors = []
    assert_key_value('Credit Balance Alert',
                     nf_resp,
                     config_key=NfKeys.TITLE.value,
                     errors_list=errors)

    assert_key_value('You have run out of usage credits. '
                     'To continue using AI Platform please '
                     'buy additional credits.',
                     nf_resp,
                     config_key=NfKeys.DESCRIPTION.value,
                     errors_list=errors)

    assert_key_value(f'{env_params[1]}/usage',
                     nf_resp,
                     config_key=NfKeys.LINK.value,
                     errors_list=errors)

    assert_key_value('credits_system.empty_balance',
                     nf_resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors)

    # pushNotificationSent is False
    assert_bool_key(False,
                    nf_resp,
                    config_key=NfKeys.PUSH_NF_SENT.value,
                    errors_list=errors)

    # Notification is not read
    assert_bool_key(False,
                    nf_resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors)

    # TODO: uncomment read notification code once SELF-2407 is fixed
    # Read Credit Balance Alert notification
    # app_client.v2_read_notification(
    #     resp_key_by_dynamic_json_path(nf_resp, NfKeys.ID.value))
    # nf_resp = app_client.v2_get_user_notifications()

    # Notification is read now
    # assert_bool_key(True,
    #                 nf_resp,
    #                 config_key=NfKeys.READ.value,
    #                 errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.credits_system
@mark.trial
def test_0_balance_cannot_make_batch_predictions(out_of_credits_setup,
                                                 assert_limited_access):

    app_client, _, _, _, deployment_id, dataset_id, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_make_batch_predictions(deployment_id, dataset_id)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_upload_dataset(out_of_credits_setup,
                                         assert_limited_access):

    app_client, _, _, _, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_upload_dataset_via_url(TEN_K_DIABETES_XLSX_DATASET)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_create_project(out_of_credits_setup,
                                         assert_limited_access):

    app_client, _, _, _, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_create_project_from_file(TEN_K_DIABETES_DATASET)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_train_model(out_of_credits_setup,
                                      assert_limited_access):

    app_client, project_id, bp_id, _, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_train_model(project_id, bp_id)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_start_autopilot(out_of_credits_setup,
                                          assert_limited_access):

    app_client, project_id, _, _, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_start_autopilot(project_id,
                                      TEN_K_DIABETES_TARGET,
                                      ModelingMode.QUICK.value)
    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_deploy_model(out_of_credits_setup,
                                       assert_limited_access):

    app_client, _, _, model_id, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_deploy_from_learning_model(model_id)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_deploy_automodel(out_of_credits_setup,
                                           assert_limited_access):

    app_client, project_id, _, _, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_deploy_automodel('Automodel label',
                                       project_id)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_create_ai_app(out_of_credits_setup,
                                        assert_limited_access):

    app_client, project_id, _, _, deployment_id, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_create_ai_app(app_name='What If app',
                                    deployment_id=deployment_id)
    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_delete_deployment(out_of_credits_setup,
                                            assert_limited_access):

    app_client, _, _, _, deployment_id, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_delete_deployment(deployment_id)

    assert_limited_access(error)


@mark.credits_system
@mark.trial
def test_0_balance_cannot_delete_project(out_of_credits_setup,
                                         assert_limited_access):

    app_client, project_id, _, _, _, _, _ = out_of_credits_setup

    with raises(AssertionError) as error:
        app_client.v2_delete_project_by_project_id(project_id)

    assert_limited_access(error)


def grant_a_credit_if_0(app_client, dr_account_client):
    """Grant 1 credit to a user if current_balance <= 0"""
    current_balance = app_client.v2_get_current_credit_balance()
    if current_balance <= 0:
        dr_account_client.admin_adjust_balance(1)
    else:
        LOGGER.info(
            'No need to increase balance. Current balance: %d',
            current_balance)
