from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ASSERT_ERRORS,
    TEN_K_DIABETES_TARGET
)
from utils.selectors_enums import (
    NewPageSelectors,
    AiProfilePageSelectors,
    HomePageSelectors,
    DataPageSelectors,
    DeploymentsPageSelectors
)
from utils.data_enums import (
    Envs,
    FeatureFlags
)
from utils.ui_constants import COMPUTE_PREDICTIONS_BUTTON


@mark.ui
def test_smoke(setup_user, new_page, data_page, home_page,
               assert_demo_datasets, assert_button_is_disabled,
               create_ai_profile, assert_balance_at_home_page,
               assert_home_page_card_is_selected,
               start_10k_diabetes_demo_dataset_modeling,
               deploy_model_from_detailed_view,
               make_predictions_for_demo_project,
               create_app_from_automodel,
               top_menu_page, models_page, deployments_page, apps_page,
               browser_context_args):
    # -----------------------------------------------------
    # 1. Create Developer profile
    # -----------------------------------------------------
    create_ai_profile(
        AiProfilePageSelectors.DEVELOPER.value,
        AiProfilePageSelectors.MANUFACTURING.value,
        AiProfilePageSelectors.CREATE_MODELS.value)

    # Assertion errors will be stored in errors list
    errors = []

    home_page.close_pendo_tour_if_present()
    # -----------------------------------------------------
    # 2. Assert Home page balance is 20,000
    # -----------------------------------------------------
    assert_balance_at_home_page('20,000', errors)

    # -----------------------------------------------------
    # 3. Assert ML Development card is selected at Home page
    # -----------------------------------------------------
    assert_home_page_card_is_selected(
        HomePageSelectors.ML_DEV_CARD.value, errors
    )
    home_page.continue_from_ml_dev()

    # -----------------------------------------------------
    # 4. Assert HDFS button is disabled at /new page
    # -----------------------------------------------------
    assert_button_is_disabled(
        new_page, NewPageSelectors.HDFS_BUTTON.value, errors,
        help_text='HDFS button must be disabled'
    )
    # -----------------------------------------------------
    # 5. Assert there are 13 demo datasets
    # -----------------------------------------------------
    assert_demo_datasets(errors)

    # -----------------------------------------------------
    # 6. Start modeling for Hospital Readmission demo project
    # -----------------------------------------------------
    start_10k_diabetes_demo_dataset_modeling(errors)

    # -----------------------------------------------------
    # 7. Wait for EDA is done
    # -----------------------------------------------------
    data_page.wait_for_eda_is_done()

    top_menu_page.go_to_models_page()
    # -----------------------------------------------------
    # 8. Deploy model
    # -----------------------------------------------------
    deploy_model_from_detailed_view(
        models_page.random_forest_classifier_gini_model_title)

    deployments_page.click_element(deployments_page.predictions_tab)
    # -----------------------------------------------------
    # 9. Make predictions
    # -----------------------------------------------------
    make_predictions_for_demo_project(errors)

    top_menu_page.go_to_models_page()
    # -----------------------------------------------------
    # 10. Deploy Automodel
    # -----------------------------------------------------
    models_page.deploy_automodel()

    top_menu_page.go_to_deployments_page()
    # -----------------------------------------------------
    # 11. Close MLOps Splash modal
    # -----------------------------------------------------
    deployments_page.close_mlops_splash_modal()

    # TODO: UI for apps creation has changed. Need to update steps 12 and 13
    # -----------------------------------------------------
    # 12. Create What If app from Automodel
    # -----------------------------------------------------
    # create_app_from_automodel(DeploymentsPageSelectors.WHAT_IF_APP.value)

    # -----------------------------------------------------
    # 13. Open What If app
    # -----------------------------------------------------
    # what_if_page = apps_page.open_app('What If', WhatIfAppPage)
    # what_if_page.wait_for_element(
    #     WhatIfAppPageSelectors.MANAGE_VARIABLES_TEXT.value)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def setup_user(payg_drap_user_setup_teardown,
               env_params,
               grant_credits,
               sign_in_user,
               add_feature_flags):
    """
    Sets up test PayAsYouGoUser:
    1. Create PayAsYouGoUser with DRAP account
    2. Add some onboarding flags for staging env
    3. Grant user 20000 credits
    4. Sign in user
    5. Delete user and apps at the end of the test
    """
    app_client, _, username, _, _ = payg_drap_user_setup_teardown

    if Envs.STAGING.value in env_params[0]:
        add_feature_flags(
            {FeatureFlags.ENABLE_PLATFORM_QUESTIONNAIRE.value: True}
        )
    grant_credits(20000)

    sign_in_user(username)

    yield app_client

    app_client.v2_delete_user_apps()


@fixture
def assert_demo_datasets(new_page):
    """Assert there are 14 demo datasets"""

    def assert_demo_datasets(errors_list):
        expected_count = 13
        actual_count = len(
            new_page.get_child_elements_by_selector(
                NewPageSelectors.DEMO_DATASETS_LIST.value
            ))
        if actual_count < expected_count or actual_count > expected_count+1:
            errors_list.append(
                f'Expected {expected_count} demo datasets,'
                f' got: {actual_count}')

    return assert_demo_datasets


@fixture
def start_10k_diabetes_demo_dataset_modeling(
        new_page, data_page, assert_inner_text_equals):
    """
    Start modeling with Hospital Readmission demo dataset:
    1. Import demo dataset
    2. Set 'readmitted' target
    3. Assert modeling mode is Quick
    4. Start modeling
    """
    def start_modeling(errors_list):
        new_page.import_demo_dataset(
            new_page.hospital_readmission_import_button
        )
        data_page.enter_recommended_target(
            TEN_K_DIABETES_TARGET
        )
        assert_inner_text_equals(
            data_page,
            DataPageSelectors.SELECTED_MODELING_MODE.value,
            'Quick',
            errors_list,
            'Wrong modeling mode!'
        )
        data_page.start_modeling()

    return start_modeling


@fixture
def deploy_model_from_detailed_view(top_menu_page,
                                    models_page):
    """
    Deploys model from model detailed view:
    1. Open model detailed view
    2. Wait until Predict tab is enabled
    3. Go to Predict -> Deploy tab
    4. Deploy model
    """
    def deploy_model_from_ui(model_title):
        models_page.expand_model(model_title)
        models_page.poll_for_predict_tab_enabled()
        models_page.click_element(models_page.predict_tab)
        models_page.click_element(models_page.deploy_tab)
        models_page.deploy_model()

    return deploy_model_from_ui


@fixture
def make_predictions_for_demo_project(assert_button_is_disabled,
                                      deployments_page):
    """
    Makes predictions for a demo project:
    1. Downloads predictions sample dataset
    2. Uploads downloaded predictions sample dataset to make predictions
    3. Computes and downloads predictions.
    """
    def make_predictions(errors_list):

        sample_file_name =\
            deployments_page.download_predictions_sample_dataset()
        assert_button_is_disabled(
            deployments_page,
            DeploymentsPageSelectors.COMPUTE_DOWNLOAD_PREDICTIONS_BUTTON.value,
            errors_list,
            f'{COMPUTE_PREDICTIONS_BUTTON} must be disabled '
            f'after downloading sample predictions dataset.'
        )
        deployments_page.upload_predictions_dataset(sample_file_name)
        deployments_page.compute_and_download_predictions()

    return make_predictions


@fixture
def create_app_from_automodel(deployments_page):
    """
    Creates App from Automodel deployment:
    1. Expand Automodel deployment
    2. Open deployment actions menu
    3. Create app
    """
    def create_app(app_selector):
        deployments_page.expand_automodel_deployment()
        deployments_page.open_deployment_actions_menu()
        deployments_page.create_app(app_selector)

    return create_app
