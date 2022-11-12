import logging
from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ASSERT_ERRORS,
    ANIMALS_DATASET,
    TEN_K_DIABETES_TARGET,
    TEN_K_DIABETES_PROJECT_NAME
)
from utils.data_enums import (
    FeatureFlags,
    Envs
)
from utils.selectors_enums import (
    AiProfilePageSelectors,
    HomePageSelectors,
    DataPageSelectors,
    DeploymentsPageSelectors
)
from pages import PaxataLoginPage


LOGGER = logging.getLogger(__name__)


ML_DEV_CARD = 'ML Dev card'
ML_DEV_TRACK = 'ML Dev learning track'
DATA_PREP_CARD = 'Data Preparation card'
DATA_PREP_TRACK = 'Data Preparation learning track'
ML_OPS_CARD = 'ML Ops card'
ML_OPS_TRACK = 'ML Ops learning track'
ANIMALS = 'animals.csv'


@mark.ui
def test_ai_platform_home(setup_user, home_page,
                          assert_home_page_card_is_selected,
                          validate_content, app_client,
                          top_menu_page, models_page,
                          click_recent_deployment,
                          click_animals_recent_project):

    # Assertion errors will be stored in errors list
    errors = []

    # -----------------------------------------------------------------------
    # 1. ML Dev card is selected
    # -----------------------------------------------------------------------
    assert_home_page_card_is_selected(HomePageSelectors.ML_DEV_CARD.value, errors)

    # -----------------------------------------------------------------------
    # 2. Validate content of ML Dev learning track
    # -----------------------------------------------------------------------
    validate_content(errors, ML_DEV_TRACK, ML_DEV_TRACK_CONTENT)

    # -----------------------------------------------------------------------
    # 3. Validate content of ML Dev card
    # -----------------------------------------------------------------------
    validate_content(errors, ML_DEV_CARD, ML_DEV_CARD_CONTENT)

    # -----------------------------------------------------------------------
    # 4. Validate content of ML Ops learning track
    # -----------------------------------------------------------------------
    home_page.select_learning_track_card(home_page.ml_ops_card)
    validate_content(errors, ML_OPS_TRACK, ML_OPS_TRACK_CONTENT)

    # -----------------------------------------------------------------------
    # 5. Validate content of ML Ops card
    # -----------------------------------------------------------------------
    validate_content(errors, ML_OPS_CARD, ML_OPS_CARD_CONTENT)

    # -----------------------------------------------------------------------
    # 6. Validate content of Data Preparation learning track
    # -----------------------------------------------------------------------
    home_page.select_learning_track_card(home_page.data_prep_card)
    validate_content(errors, DATA_PREP_TRACK, DATA_PREP_TRACK_CONTENT)

    # -----------------------------------------------------------------------
    # 7. Validate content of Data Preparation card
    # -----------------------------------------------------------------------
    validate_content(errors, DATA_PREP_CARD, DATA_PREP_CARD_CONTENT)

    # -----------------------------------------------------------------------
    # 8. Paxata login page is opened after clicking Continue button
    #    from Data Preparation card
    # -----------------------------------------------------------------------
    home_page.continue_to_paxata_login_from_data_prep_card(PaxataLoginPage)

    # -----------------------------------------------------------------------
    # 9. Redirected to /new page after clicking Continue button from ML Dev card
    # -----------------------------------------------------------------------
    home_page.select_learning_track_card(home_page.ml_dev_card)
    home_page.continue_to_new_page_from_ml_dev_card()

    # -----------------------------------------------------------------------
    # 10. Start animals.csv project creation and validate ML Dev Recent Projects
    #     section before setting a target
    # -----------------------------------------------------------------------
    animals_project_id = app_client.v2_create_project_from_file(ANIMALS_DATASET)
    top_menu_page.go_to_home_page_by_clicking_dr_logo_icon()
    home_page.close_pendo_tour_if_present()
    validate_content(
        errors, f'Recent Projects: {ANIMALS}', RECENT_PROJECTS_ANIMALS)

    # -----------------------------------------------------------------------
    # 11. Redirected to Set target page after clicking animals.scv
    #     project name from ML Dev Recent Projects section
    # -----------------------------------------------------------------------
    click_animals_recent_project(animals_project_id)

    # -----------------------------------------------------------------------
    # 12. Start a new project 10k_diabetes modeling in manual mode,
    #     deploy Auto-tuned K-Nearest Neighbors Classifier (Euclidean Distance)
    #     model and validate Recent Projects section
    # -----------------------------------------------------------------------
    _, _, _, deployment_id = app_client.setup_10k_diabetes_project()
    top_menu_page.go_to_home_page_by_clicking_dr_logo_icon()
    validate_content(
        errors, f'Recent Projects: {TEN_K_DIABETES_PROJECT_NAME}',
        RECENT_PROJECTS_DIABETES)

    # -----------------------------------------------------------------------
    # 13. Redirected to /new page after clicking 'Create new project' button
    #     from Recent Projects section
    # -----------------------------------------------------------------------
    home_page.close_pendo_tour_if_present()
    home_page.click_create_new_project_button()

    models_page.navigate_to_ai_platform_page()
    home_page.select_learning_track_card(home_page.ml_ops_card)
    # -----------------------------------------------------------------------
    # 14. Validate Recent Deployments section of ML Ops track
    # -----------------------------------------------------------------------
    validate_content(errors, f'Recent Deployments', RECENT_DEPLOYMENTS_CONTENT)

    # -----------------------------------------------------------------------
    # 15. Redirected to MLOps page after clicking 'Go to MLOps' button
    #     from MLOps track
    # -----------------------------------------------------------------------
    home_page.click_go_to_mlops_button()

    top_menu_page.go_to_home_page_by_clicking_dr_logo_icon()
    # -----------------------------------------------------------------------
    # 16. Redirected to deployments/<deployment_id>/overview page after
    #     clicking recent deployment from Recent Deployments section
    # -----------------------------------------------------------------------
    click_recent_deployment(deployment_id)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def setup_user(payg_drap_user_setup_teardown,
               env_params, grant_credits,
               sign_in_user, add_feature_flags,
               create_ai_profile, home_page):
    """
    Sets up test PayAsYouGoUser:
    1. Creates PayAsYouGoUser with DRAP account
    2. Adds ENABLE_PLATFORM_QUESTIONNAIRE flag for staging env
    3. Grants user 20000 credits
    4. Signs in user
    5. Creates Developer AI Profile
    5. Closes Pendo Home tour if present
    """
    app_client, _, username, _, _ = payg_drap_user_setup_teardown
    if Envs.STAGING.value in env_params[0]:
        add_feature_flags(
            {FeatureFlags.ENABLE_PLATFORM_QUESTIONNAIRE.value: True})
    grant_credits(20000)

    sign_in_user(username)
    create_ai_profile(
        AiProfilePageSelectors.DEVELOPER.value,
        AiProfilePageSelectors.MANUFACTURING.value,
        AiProfilePageSelectors.CREATE_MODELS.value
    )
    home_page.close_pendo_tour_if_present()


@fixture
def validate_content(home_page, assert_element_is_present):
    """Asserts piece of content list is present."""

    def validate_content(errors_list, content_title, content):

        for content_piece in content:
            assert_element_is_present(
                home_page, content_piece, errors_list, f'Check {content_title} content')

    return validate_content


@fixture
def click_animals_recent_project(home_page, data_page):
    """
    Clicks animals.csv project name from Recent Projects section.
    Waits until user is redirected to /data page by checking that Enter target field is present.
    Asserts that project_id is in data_page.page_url.
    """
    def click_animals_recent_project(project_id):

        home_page.click_selector(RecentProjectsSelectors.ANIMALS_PROJECT_NAME.value)
        data_page.wait_for_element(DataPageSelectors.ENTERED_TARGET.value)
        if project_id not in data_page.page_url:
            raise ValueError(
                f'Project ID {project_id} is not in {data_page.page_url}. '
                f'User must be redirected to projects/<project_id>/eda page'
            )
        LOGGER.info(
            'Redirected to %s page after clicking animals.csv from Recent Projects',
            data_page.page_url)

    return click_animals_recent_project


@fixture
def click_recent_deployment(home_page, deployments_page):
    """
    Clicks recent deployment from Recent Deployments section.
    Waits until user is redirected to deployments/<deployment_id>/overview page by checking that
    DEPLOYMENT_CREATED_TILE element is present.
    Asserts that deployment_id is in deployments_page.page_url.
    """
    def click_recent_deployment(deployment_id):

        home_page.click_selector(HomePageSelectors.RECENT_DEPLOYMENTS_DEPLOYMENT_NAME.value)
        deployments_page.wait_for_element(DeploymentsPageSelectors.DEPLOYMENT_CREATED_TILE.value)
        if deployment_id not in deployments_page.page_url:
            raise ValueError(
                f'Deployment ID {deployment_id} is not in {deployments_page.page_url}. '
                f'User must be redirected to deployments/<deployment_id>/overview page'
            )
        LOGGER.info(
            'Redirected to %s page after clicking deployment name from Recent Deployments',
            deployments_page.page_url)

    return click_recent_deployment


class RecentProjectsSelectors(Enum):

    PROJECT_NAME_CONTAINER = 'div.project-name-container'
    DATASET_SELECTOR = 'div.r-td.file-name-cell'
    TABLE_ROW = 'div.r-td'
    ANIMALS_PROJECT_NAME = f'{HomePageSelectors.RECENT_PROJECTS_TABLE.value} >> ' \
                           f'{PROJECT_NAME_CONTAINER} ' \
                           f':has-text("{ANIMALS}")'
    DIABETES_PROJECT_NAME = f'{HomePageSelectors.RECENT_PROJECTS_TABLE.value} >> ' \
                            f'{PROJECT_NAME_CONTAINER} ' \
                            f':has-text("{TEN_K_DIABETES_PROJECT_NAME}")'
    ANIMALS_DATASET_NAME = f'{HomePageSelectors.RECENT_PROJECTS_TABLE.value} >> ' \
                           f'{DATASET_SELECTOR} ' \
                           f':has-text("{ANIMALS}")'
    DIABETES_DATASET_NAME = f'{HomePageSelectors.RECENT_PROJECTS_TABLE.value} >> ' \
                            f'{DATASET_SELECTOR} ' \
                            f':has-text("{TEN_K_DIABETES_PROJECT_NAME}")'
    DIABETES_MODEL_TYPE = f'{HomePageSelectors.RECENT_PROJECTS_TABLE.value} >> ' \
                          f'{TABLE_ROW} ' \
                          f':has-text("Binary")'
    DIABETES_TARGET = f'{HomePageSelectors.RECENT_PROJECTS_TABLE.value} >> ' \
                      f'{TABLE_ROW} ' \
                      f':has-text("{TEN_K_DIABETES_TARGET}")'


ML_DEV_TRACK_CONTENT = [
    HomePageSelectors.ML_DEV_TRACK_TITLE.value,
    HomePageSelectors.ML_DEV_TRACK_ROBOT_ICON.value,
    HomePageSelectors.ML_DEV_CONTINUE_BUTTON.value,
    HomePageSelectors.ML_DEV_TRACK_DESCRIPTION.value,
    HomePageSelectors.ML_DEV_SELECT_USE_CASE_STEP.value,
    HomePageSelectors.ML_DEV_SET_TARGET_STEP.value,
    HomePageSelectors.ML_DEV_EXPLORE_DATA_STEP.value,
    HomePageSelectors.ML_DEV_COMPARE_MODELS_STEP.value,
    HomePageSelectors.ML_DEV_CREATE_DEPLOY_STEP.value,
    HomePageSelectors.ML_DEV_PREDICTIONS_STEP.value,
    HomePageSelectors.ML_DEV_AI_APP_STEP.value,
]
DATA_PREP_TRACK_CONTENT = [
    HomePageSelectors.DATA_PREP_TRACK_TITLE.value,
    HomePageSelectors.DATA_PREP_TRACK_ROBOT_ICON.value,
    HomePageSelectors.DATA_PREP_CONTINUE_BUTTON.value,
    HomePageSelectors.DATA_PREP_TRACK_DESCRIPTION.value,
    HomePageSelectors.DATA_PREP_SELECT_DATA_SOURCE_STEP.value,
    HomePageSelectors.DATA_PREP_COMBINE_ENRICH_STEP.value,
    HomePageSelectors.DATA_PREP_CLEANUP_DATA_STEP.value,
    HomePageSelectors.DATA_PREP_TARGET_VAR_STEP.value,
    HomePageSelectors.DATA_PREP_EXPORT_TO_ML_DEV_STEP.value,
]
ML_OPS_TRACK_CONTENT = [
    HomePageSelectors.ML_OPS_TRACK_TITLE.value,
    HomePageSelectors.ML_OPS_TRACK_ROBOT_ICON.value,
    HomePageSelectors.ML_OPS_CONTINUE_BUTTON.value,
]
ML_DEV_CARD_CONTENT = [
    HomePageSelectors.ML_DEV_CARD_ICON.value,
    HomePageSelectors.ML_DEV_CARD_TITLE.value,
    HomePageSelectors.ML_DEV_CARD_DESCRIPTION.value,
]
DATA_PREP_CARD_CONTENT = [
    HomePageSelectors.DATA_PREP_CARD_ICON.value,
    HomePageSelectors.DATA_PREP_CARD_TITLE.value,
    HomePageSelectors.DATA_PREP_CARD_DESCRIPTION.value,
]
ML_OPS_CARD_CONTENT = [
    HomePageSelectors.ML_OPS_CARD_ICON.value,
    HomePageSelectors.ML_OPS_CARD_TITLE.value,
    HomePageSelectors.ML_OPS_CARD_DESCRIPTION.value,
]
RECENT_PROJECTS_ANIMALS = [
    HomePageSelectors.RECENT_PROJECTS_TITLE.value,
    HomePageSelectors.CREATE_NEW_PROJECT_BUTTON.value,
    HomePageSelectors.RECENT_PROJECTS_PROJECT_NAME_COLUMN.value,
    HomePageSelectors.RECENT_PROJECTS_DATASET_COLUMN.value,
    HomePageSelectors.RECENT_PROJECTS_MODEL_TYPE_COLUMN.value,
    HomePageSelectors.RECENT_PROJECTS_TARGET_COLUMN.value,
    RecentProjectsSelectors.ANIMALS_PROJECT_NAME.value,
    RecentProjectsSelectors.ANIMALS_DATASET_NAME.value,
]
RECENT_PROJECTS_DIABETES = [
    RecentProjectsSelectors.DIABETES_PROJECT_NAME.value,
    RecentProjectsSelectors.DIABETES_DATASET_NAME.value,
    RecentProjectsSelectors.DIABETES_MODEL_TYPE.value,
    RecentProjectsSelectors.DIABETES_TARGET.value,
]
RECENT_DEPLOYMENTS_CONTENT = [
    HomePageSelectors.RECENT_DEPLOYMENTS_TITLE.value,
    HomePageSelectors.GO_TO_MLOPS_BUTTON.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_DEPLOYMENT_NAME_COLUMN.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_ACTIVITY_COLUMN.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_PREDICTION_COLUMN.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_DEPLOYMENT_NAME.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_PREDICTION_SERVER.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_ACTIVITY_GRAPH.value,
    HomePageSelectors.RECENT_DEPLOYMENTS_LAST_PREDICTION.value,
]
