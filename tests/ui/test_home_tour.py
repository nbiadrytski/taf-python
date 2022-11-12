from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import ASSERT_ERRORS
from utils.selectors_enums import (
    ToursGuideSelectors,
    AiProfilePageSelectors,
    TEXT,
    TOOLTIP_TEXT_CLASS_VALUE
)
from utils.data_enums import (
    Envs,
    FeatureFlags
)


@mark.ui
def test_home_tour(
        setup_and_sign_in_payg_user, home_page, pendo_tour_page,
        assert_tooltip_content, assert_robot_icon_state,
        assert_announcements_count, assert_announcement, tours_guide_component,
        assert_tooltip_multi_content, go_to_next_tour_slide
):
    setup_and_sign_in_payg_user()
    # Assertion errors will be stored in errors list
    errors = []

    pendo_tour_page.start_home_tour()

    # -------------------------------------------------------------------
    # 1. Validate PREPARE YOUR DATASET tooltip
    # -------------------------------------------------------------------
    assert_tooltip_content(
        HomeTourTooltipSelectors.DATA_PREP_TITLE.value,
        HomeTourTooltipSelectors.DATA_PREP_TEXT.value,
        errors, start_tour=False, check_back_close_buttons=True, click_next=False)

    # -------------------------------------------------------------------
    # 2. Validate BUILD MACHINE LEARNING MODELS tooltip
    # -------------------------------------------------------------------
    assert_tooltip_content(
        HomeTourTooltipSelectors.ML_DEV_TITLE.value,
        HomeTourTooltipSelectors.ML_DEV_TEXT.value,
        errors, start_tour=False, check_back_close_buttons=True)

    # -------------------------------------------------------------------
    # 3. Validate MANAGE PRODUCTION MODELS tooltip
    # -------------------------------------------------------------------
    go_to_next_tour_slide(HomeTourTooltipSelectors.ML_OPS_TITLE.value)
    assert_tooltip_multi_content(
        errors, ML_OPS_TOOLTIP_TITLE, ML_OPS_TOOLTIP_CONTENT,
        check_back_button=True)

    # -------------------------------------------------------------------
    # 4. Validate ACCOUNT SETTINGS tooltip
    # -------------------------------------------------------------------
    assert_tooltip_content(
        HomeTourTooltipSelectors.ACCOUNT_TITLE.value,
        HomeTourTooltipSelectors.ACCOUNT_TEXT.value,
        errors, start_tour=False, check_back_close_buttons=True)

    # -------------------------------------------------------------------
    # 5. Validate LOOKING FOR SUPPORT? tooltip
    # -------------------------------------------------------------------
    assert_tooltip_content(
        HomeTourTooltipSelectors.SUPPORT_TITLE.value,
        HomeTourTooltipSelectors.SUPPORT_TEXT.value,
        errors, start_tour=False, check_back_close_buttons=True)

    # -------------------------------------------------------------------
    # 6. Validate End Of Tour page content
    # -------------------------------------------------------------------
    go_to_next_tour_slide(HomeTourTooltipSelectors.LAST_PAGE_TITLE.value)
    assert_tooltip_multi_content(
        errors, HomeTourTooltipSelectors.LAST_PAGE_TITLE.value,
        LAST_PAGE_TOOLTIP_CONTENT, check_back_button=False)

    pendo_tour_page.click_was_tour_helpful_yes_button()

    # -------------------------------------------------------------------
    # 7. Robot icon with 2 notifications badge is present
    # -------------------------------------------------------------------
    assert_robot_icon_state(errors, nf_count=2)

    # -------------------------------------------------------------------
    # 8. Tour Guide has 2 Announcements
    # -------------------------------------------------------------------
    tours_guide_component.open_tours_guide()
    assert_announcements_count(errors, count=2)

    # -------------------------------------------------------------------
    # 9. Validate content of Build AI Models and Explore Model Insights
    #     announcements
    # -------------------------------------------------------------------
    tours_guide_component.open_announcements()
    assert_announcement(errors, content=BUILD_MODELS_ANNOUNCE)
    assert_announcement(errors, content=EXPLORE_MODEL_INSIGHTS_ANNOUNCE)

    tours_guide_component.return_from_tour_announcements_details()
    # -------------------------------------------------------------------
    # 10. Robot icon badge has 1 notification after opening
    #     announcements list
    # -------------------------------------------------------------------
    assert_robot_icon_state(errors, nf_count=1)

    # -------------------------------------------------------------------
    # 11. Announcements count is 1 after opening announcements list
    # -------------------------------------------------------------------
    tours_guide_component.return_from_tour_announcements_details()
    assert_announcements_count(errors, count=1)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def setup_and_sign_in_payg_user(
        payg_drap_user_setup_teardown, env_params, grant_credits, sign_in_user,
        new_page, home_page, create_ai_profile
):
    """
    Sets up PayAsYouGoUser:
    1. Creates PayAsYouGoUser with DRAP account
    2. Grants credits to the user
    3. Signs in user
    4. Creates AI profile
    """
    def setup_and_sign_in_user(
            credits_amount=20000,
            role=AiProfilePageSelectors.DEVELOPER.value,
            industry=AiProfilePageSelectors.GAMING.value,
            learning_track=AiProfilePageSelectors.CREATE_MODELS.value):

        app_client, user_id, username, _, _ = payg_drap_user_setup_teardown

        if Envs.STAGING.value in env_params[0]:
            app_client.v2_add_feature_flag(
                FeatureFlags.ENABLE_PLATFORM_QUESTIONNAIRE.value
            )
        grant_credits(credits_amount)

        sign_in_user(username)
        create_ai_profile(role, industry, learning_track)

        return user_id

    return setup_and_sign_in_user


@fixture
def assert_robot_icon_state(
        home_page, tours_guide_component, assert_element_is_present
):
    """Asserts that Robot icon with N notifications badge is present."""

    def robot_icon_state(errors_list, nf_count):

        assert_element_is_present(
            home_page, ToursGuideSelectors.ROBOT_ICON.value, errors_list,
            'No Robot icon in bottom right corner after last slide was closed'
        )
        count = tours_guide_component.get_robot_icon_notifications_count()
        if count != str(nf_count):
            errors_list.append(
                f'Expected notifications count: {nf_count}, got: {count}')

    return robot_icon_state


@fixture
def assert_announcements_count(tours_guide_component):
    """Asserts number of announcements at Tour Guide badge."""

    def announcements_count(errors_list, count):

        actual_count = tours_guide_component.get_announcements_count()
        if actual_count != str(count):
            errors_list.append(
                f'Expected Announcements count: {count}, got: {actual_count}.')

    return announcements_count


@fixture
def assert_announcement(tours_guide_component, assert_element_is_present):
    """
    Asserts announcement content and
    if its 'Launch Tour' button is present.
    """
    def announcement(errors_list, content):

        assert_element_is_present(
            tours_guide_component,
            ToursGuideSelectors.ANNOUNCEMENT_CONTENT.value.format(content),
            errors_list,
            f'Announcement: "{content}" is either incorrect or absent')

    return announcement


class HomeTourTooltipSelectors(Enum):
    # Start page
    START_PAGE_TEXT1 = TEXT.format(
        'AI Platform Home is a launch point for driving better business '
        'outcomes with')
    START_PAGE_TEXT2 = TEXT.format(
        'the DataRobot platform. From here you can prepare datasets and '
        'build models')
    START_PAGE_TEXT3 = TEXT.format(
        'as well as deploy, monitor, and manage your models in production. '
        'Follow this')
    START_PAGE_TEXT4 = TEXT.format(
        'short tour to learn how to access these tools and where to find help'
        ' if you need it')

    # PREPARE YOUR DATASET
    DATA_PREP_TITLE = TEXT.format('Prepare your dataset')
    DATA_PREP_TEXT = TEXT.format(
        'Data not quite ready? Use our data preparation capabilities to '
        'explore, profile, clean, enrich, and shape '
        'your data into assets optimized for machine learning.')

    # BUILD MACHINE LEARNING MODELS
    ML_DEV_TITLE = TEXT.format('BUILD MACHINE LEARNING MODELS')
    ML_DEV_TEXT = TEXT.format(
        'DataRobot\'s industry-leading platform helps you build models from '
        'your prepared data and explore the insights those models provide. '
        'Need a dataset to get started? Start a new project and try our '
        'demo datasets to explore the power of AutoML.')

    # MANAGE PRODUCTION MODELS
    ML_OPS_TITLE = TEXT.format('Manage Production Models')
    ML_OPS_TEXT1 = TEXT.format(
        'Manage and govern your production models from a central location, '
        'whether DataRobot-built or not.')
    ML_OPS_TEXT2 = TEXT.format(
        'Deploy them to any prediction environment—internal or ')
    ML_OPS_TEXT3 = TEXT.format('external—and monitor them from ML Operations.')

    # ACCOUNT SETTINGS
    ACCOUNT_TITLE = TEXT.format('ACCOUNT SETTINGS')
    ACCOUNT_TEXT = TEXT.format(
        'Update your profile, choose display and notification settings, '
        'or set up your auth token to integrate with our APIs. Monitoring '
        'external models? Find the agent here.')

    # LOOKING FOR SUPPORT?
    SUPPORT_TITLE = TEXT.format('LOOKING FOR SUPPORT?')
    SUPPORT_TEXT = TEXT.format(
        'Browse our comprehensive documentation or find answers in the '
        'DataRobot Community.')

    # Last page
    LAST_PAGE_TITLE = TEXT.format('Let the journey begin!')
    LAST_PAGE_TEXT1 = TEXT.format(
        'Select your preferred tile and follow the links to start creating '
        'amazing and insightful AI with DataRobot, or to jump right in with '
        'step-by-step assistance click the ')
    LAST_PAGE_TEXT2 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("robot menu ")'
    LAST_PAGE_TEXT3 = TEXT.format('in the bottom right corner.')
    LAST_PAGE_COMMUNITY_LINK = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                               f'[href="https://community.datarobot.com"]'


ML_OPS_TOOLTIP_TITLE = 'MANAGE PRODUCTION MODELS'
ML_OPS_TOOLTIP_CONTENT = [
            HomeTourTooltipSelectors.ML_OPS_TEXT1.value,
            HomeTourTooltipSelectors.ML_OPS_TEXT2.value,
            HomeTourTooltipSelectors.ML_OPS_TEXT3.value,
        ]
LAST_PAGE_TOOLTIP_CONTENT = [
        HomeTourTooltipSelectors.LAST_PAGE_TEXT1.value,
        HomeTourTooltipSelectors.LAST_PAGE_TEXT2.value,
        HomeTourTooltipSelectors.LAST_PAGE_TEXT3.value,
        HomeTourTooltipSelectors.LAST_PAGE_COMMUNITY_LINK.value]


BUILD_MODELS_ANNOUNCE = 'Ready to build AI models? Check out the latest ' \
                        'onboarding tour by clicking the button below or ' \
                        'navigating to \'Onboarding Tours\' in the robot menu!'
EXPLORE_MODEL_INSIGHTS_ANNOUNCE = 'Want to see the different ways to get ' \
                                  'insights from a model? Check out the ' \
                                  'Explore Model Insights onboarding tour. '
