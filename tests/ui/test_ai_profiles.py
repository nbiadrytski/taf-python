from pytest import (
    mark,
    fixture
)

from utils.selectors_enums import (
    HomePageSelectors,
    AiProfilePageSelectors
)
from utils.data_enums import (
    Envs,
    FeatureFlags
)
from utils.constants import ASSERT_ERRORS


CARD_NOT_SELECTED = '{} card is not selected'


@mark.ui
def test_analyst_explore_insights_profile(
        setup_user, create_ai_profile, assert_home_page_card_is_selected):

    # -----------------------------------------------------
    # 1. Create Analyst - explore insights profile
    # -----------------------------------------------------
    create_ai_profile(
        AiProfilePageSelectors.ANALYST.value,
        AiProfilePageSelectors.RETAIL.value,
        AiProfilePageSelectors.EXPLORE_INSIGHTS.value)

    # -----------------------------------------------------
    # 2. Assert ML Development card is selected.
    #    No 'Recommended' label for BA persona.
    # -----------------------------------------------------
    assert assert_home_page_card_is_selected(
        HomePageSelectors.ML_DEV_CARD.value, [], add_to_errors=False), \
        CARD_NOT_SELECTED.format('ML Dev')


@mark.ui
def test_data_scientist_prepare_data_profile(
        setup_user, create_ai_profile, assert_home_page_card_is_selected,
        assert_track_has_card_recommended_label, home_page):

    # Assertion errors will be stored in errors list
    errors = []

    # -----------------------------------------------------
    # 1. Create Data scientist - prepare data profile
    # -----------------------------------------------------
    create_ai_profile(
        AiProfilePageSelectors.DATA_SCIENTIST.value,
        AiProfilePageSelectors.HEALTHCARE.value,
        AiProfilePageSelectors.PREPARE_DATA.value
    )
    home_page.close_pendo_tour_if_present()

    # -----------------------------------------------------
    # 2. Assert Data Preparation card is selected
    # -----------------------------------------------------
    assert_home_page_card_is_selected(
        HomePageSelectors.PAXATA_DATA_PREP_CARD.value, errors)

    # -----------------------------------------------------
    # 3. Assert Data Preparation card has Recommended label
    # -----------------------------------------------------
    assert_track_has_card_recommended_label(
        errors, HomePageSelectors.PAXATA_DATA_PREP_CARD.value)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.ui
def test_product_manager_deploy_models_profile(
        setup_user, create_ai_profile, assert_home_page_card_is_selected,
        assert_track_has_card_recommended_label, home_page):

    errors = []

    # -----------------------------------------------------
    # 1. Create Product Manager - deploy and monitor profile
    # -----------------------------------------------------
    create_ai_profile(
        AiProfilePageSelectors.PRODUCT_MANAGER.value,
        AiProfilePageSelectors.NON_PROFIT.value,
        AiProfilePageSelectors.DEPLOY_AND_MONITOR.value
    )
    home_page.close_pendo_tour_if_present()

    # -----------------------------------------------------
    # 2. Assert MLOps card is selected
    # -----------------------------------------------------
    assert_home_page_card_is_selected(
        HomePageSelectors.ML_OPS_CARD.value, errors)

    # -----------------------------------------------------
    # 3. Assert MLOps card has Recommended label
    # -----------------------------------------------------
    assert_track_has_card_recommended_label(
        errors, HomePageSelectors.ML_OPS_CARD.value)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def setup_user(payg_drap_user_setup_teardown,
               env_params, sign_in_user, add_feature_flags):
    """
    Sets up test PayAsYouGoUser:
    1. Create PayAsYouGoUser with DRAP account
    2. Add ENABLE_PLATFORM_QUESTIONNAIRE flag for staging env
    4. Sign in user
    """
    _, _, username, _, _ = payg_drap_user_setup_teardown

    if Envs.STAGING.value in env_params[0]:
        add_feature_flags(
            {FeatureFlags.ENABLE_PLATFORM_QUESTIONNAIRE.value: True}
        )
    sign_in_user(username)
