from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import ASSERT_ERRORS
from utils.selectors_enums import (
    NewPageSelectors,
    DataPageSelectors,
    TopMenuSelectors,
    AiProfilePageSelectors,
    ModelingRightSidebarSelectors,
    TOOLTIP_TEXT_CLASS_VALUE,
    TEXT
)
from utils.data_enums import (
    Envs,
    FeatureFlags
)


@mark.ui
def test_build_models_tour(
        setup_and_sign_in_payg_user, pendo_tour_page, new_page,
        tours_guide_component, assert_tour_progress,
        assert_tour_start_page_content, assert_tooltip_multi_content,
        go_to_next_tour_slide, assert_element_is_hidden,
        assert_element_is_not_clickable, data_page, top_menu_page,
        assert_can_view_data_quality_info, modeling_right_sidebar,
        assert_workers_can_be_decreased, assert_was_tour_helpful_section,
        assert_element_is_highlighted_by_pendo,
        assert_element_is_present, models_page
):

    setup_and_sign_in_payg_user()
    # Assertion errors will be stored in errors list
    errors = []

    tours_guide_component.open_tours_guide()
    tours_guide_component.open_onboarding_tours()

    # --------------------------------------------------------------------
    # 1. Assert tour progress 0%
    # --------------------------------------------------------------------
    # TODO: expected_progress=0% once SELF-2696 is fixed
    # assert_tour_progress(
    #     errors, expected_progress=0, help_text='Tour initial progress')

    tours_guide_component.open_tour_from_tours_guide(
        tours_guide_component.build_ai_models_tour)
    # --------------------------------------------------------------------
    # 2. Assert start page content
    # --------------------------------------------------------------------
    assert_tour_start_page_content(errors, START_PAGE_TOOLTIP_CONTENT)

    # --------------------------------------------------------------------
    # 3. Assert 'Let's get the data' tooltip content
    # --------------------------------------------------------------------
    pendo_tour_page.start_tour(
        wait_for_back_button=False, tooltip_title=LETS_GET_DATA_TOOLTIP_TITLE)
    assert_tooltip_multi_content(
        errors, LETS_GET_DATA_TOOLTIP_TITLE, LETS_GET_DATA_TOOLTIP_CONTENT,
        check_back_button=False)

    # --------------------------------------------------------------------
    # 4. Assert 'Import dataset' buttons is disabled while
    #    'Let's get the data' tooltip is present
    # --------------------------------------------------------------------
    # assert_element_is_hidden(
    #     errors, new_page, NewPageSelectors.IMPORT_DATASET_BUTTON.value,
    #     help_text=f'Must be disabled at {LETS_GET_DATA_TOOLTIP_TITLE} tooltip')

    # --------------------------------------------------------------------
    # 5. Assert content of Ready, set, import! tooltip
    # --------------------------------------------------------------------
    go_to_next_tour_slide(
        BuildModelsTooltipSelectors.READY_SET_IMPORT_TITLE.value
    )
    assert_tooltip_multi_content(
        errors, BuildModelsTooltipSelectors.READY_SET_IMPORT_TITLE.value,
        READY_SET_IMPORT_TOOLTIP_CONTENT, check_back_button=False)

    # --------------------------------------------------------------------
    # 6. Assert 'Import dataset' button is highlighted while
    #    Ready, set, import! tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_highlighted_by_pendo(
        errors, new_page,
        NewPageSelectors.
            PREDICT_LATE_SHIPMENT_DEMO_DATASET_IMPORT_BUTTON.value,
        NOT_HIGHLIGHTED_MESSAGE.format(
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TITLE.value))
    # --------------------------------------------------------------------
    # 7. User can import 'Predict Whether A Shipment Will Be late'
    #    demo dataset while Ready, set, import! tooltip is present
    # --------------------------------------------------------------------
    new_page.import_demo_dataset(new_page.predict_late_shipment_import_button)

    # --------------------------------------------------------------------
    # 8. Assert content of DATA ANALYSIS IN A FLASH tooltip
    # --------------------------------------------------------------------
    data_page.wait_for_element(
        BuildModelsTooltipSelectors.DATA_ANALYSIS_TITLE.value)
    assert_tooltip_multi_content(
        errors, DATA_ANALYSIS_TOOLTIP_TITLE, DATA_ANALYSIS_TOOLTIP_CONTENT,
        check_back_button=False)

    # --------------------------------------------------------------------
    # 9. Assert 'Recommended target is: {}' button is not clickable
    #    while 'Data analysis in a flash' tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_not_clickable(
        errors, data_page, DataPageSelectors.RECOMMENDED_TARGET_BUTTON.value,
        help_text=NOT_CLICKABLE_MESSAGE.format(DATA_ANALYSIS_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 10. Assert 'Visualize the feature details' tooltip content
    # --------------------------------------------------------------------
    go_to_next_tour_slide(
        BuildModelsTooltipSelectors.FEATURE_DETAILS_TITLE.value)
    assert_tooltip_multi_content(
        errors, FEATURE_DETAILS_TOOLTIP_TITLE, FEATURE_DETAILS_TOOLTIP_CONTENT,
        check_back_button=True)

    # --------------------------------------------------------------------
    # 11. Assert 'Vendor' feature is highlighted while
    #    'Visualize the feature details' tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_highlighted_by_pendo(
        errors, new_page, DataPageSelectors.VENDOR_FEATURE.value,
        NOT_HIGHLIGHTED_MESSAGE.format(FEATURE_DETAILS_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 12. Assert 'Select target' button is not clickable while
    #     'Visualize the feature details' tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_not_clickable(
        errors, data_page,
        DataPageSelectors.SELECT_TARGET_BUTTON_RIGHT_SIDEBAR.value,
        help_text=NOT_CLICKABLE_MESSAGE.format(FEATURE_DETAILS_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 13. Assert TELL ME MORE ABOUT THE DATA tooltip content
    # --------------------------------------------------------------------
    go_to_next_tour_slide(
        BuildModelsTooltipSelectors.TELL_MORE_ABOUT_DATA_TITLE.value)
    assert_tooltip_multi_content(
        errors, TELL_MORE_ABOUT_DATA_TOOLTIP_TITLE,
        TELL_MORE_ABOUT_DATA_TOOLTIP_CONTENT, check_back_button=True)

    # --------------------------------------------------------------------
    # 14. Assert 'Explore the data' button is not clickable
    #     while TELL ME MORE ABOUT THE DATA tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_not_clickable(
        errors, data_page, DataPageSelectors.EXPLORE_DATA_BUTTON.value,
        help_text=NOT_CLICKABLE_MESSAGE.format(
            TELL_MORE_ABOUT_DATA_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 15. User is able to view Data Quality Assessment Info
    #     while TELL ME MORE ABOUT THE DATA tooltip is present
    # --------------------------------------------------------------------
    assert_can_view_data_quality_info(errors)

    # --------------------------------------------------------------------
    # 16. Assert content of WHAT WOULD YOU LIKE TO PREDICT? tooltip
    # --------------------------------------------------------------------
    go_to_next_tour_slide(
        BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TITLE.value)
    assert_tooltip_multi_content(
        errors, WHAT_TO_PREDICT_TOOLTIP_TITLE, WHAT_TO_PREDICT_TOOLTIP_CONTENT,
        check_back_button=True)

    # --------------------------------------------------------------------
    # 17. Assert 'Select target' section is highlighted by Pendo
    #     while WHAT WOULD YOU LIKE TO PREDICT? tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_present(
        data_page,
        DataPageSelectors.SELECT_TARGET_SECTION_PENDO_HIGHLIGHTED.value,
        errors, NOT_HIGHLIGHTED_MESSAGE.format(WHAT_TO_PREDICT_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 18. User is able to enter recommended target while
    #     WHAT WOULD YOU LIKE TO PREDICT? tooltip is present
    # --------------------------------------------------------------------
    data_page.enter_recommended_target('Late_delivery')

    # --------------------------------------------------------------------
    # 19. User is auto-redirected to Ready to model? tooltip after
    #     entering target. Assert content of Ready to model? tooltip
    # --------------------------------------------------------------------
    assert_tooltip_multi_content(
        errors, READY_TO_MODEL_TOOLTIP_TITLE, READY_TO_MODEL_TOOLTIP_CONTENT,
        check_back_button=False)

    # --------------------------------------------------------------------
    # 20. User can start modeling while Ready to model? tooltip is present
    # --------------------------------------------------------------------
    data_page.start_modeling()

    # --------------------------------------------------------------------
    # 21. Assert content of WHATS HAPPENING BEHIND THE CURTAIN? tooltip
    # --------------------------------------------------------------------
    data_page.wait_for_element(
        BuildModelsTooltipSelectors.BEHIND_CURTAIN_TITLE.value)
    assert_tooltip_multi_content(
        errors, BEHIND_CURTAIN_TOOLTIP_TITLE, BEHIND_CURTAIN_TOOLTIP_CONTENT,
        check_back_button=False)

    # --------------------------------------------------------------------
    # 22. Assert Project name at the top of the page is not clickable
    #     while WHATS HAPPENING BEHIND THE CURTAIN? tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_not_clickable(
        errors, data_page, TopMenuSelectors.PROJECT_NAME.value,
        help_text=NOT_CLICKABLE_MESSAGE.format(BEHIND_CURTAIN_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 23. User can pause modeling while
    #     WHATS HAPPENING BEHIND THE CURTAIN? tooltip is present
    # --------------------------------------------------------------------
    modeling_right_sidebar.wait_for_element(
        ModelingRightSidebarSelectors.PAUSE_MODELING_TASKS_BUTTON.value,
        timeout=300000  # 5 min
    )
    modeling_right_sidebar.pause_modeling_tasks()

    # --------------------------------------------------------------------
    # 24. Assert content of 'Let's take this to the next level' tooltip
    # --------------------------------------------------------------------
    go_to_next_tour_slide(
        BuildModelsTooltipSelectors.TAKE_TO_NEXT_LEVEL_TITLE.value)
    assert_tooltip_multi_content(
        errors, TAKE_TO_NEXT_LEVEL_TOOLTIP_TITLE,
        TAKE_TO_NEXT_LEVEL_TOOLTIP_CONTENT, check_back_button=True)

    # --------------------------------------------------------------------
    # 25. Assert workers count controls are highlighted while
    #     'Let's take this to the next level' tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_present(
        modeling_right_sidebar,
        ModelingRightSidebarSelectors.WORKERS_COUNT_CONTROLS.value,
        errors,
        NOT_HIGHLIGHTED_MESSAGE.format(TAKE_TO_NEXT_LEVEL_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 26. Assert Project name at the top of the page is not clickable
    #     while 'Let's take this to the next level' tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_not_clickable(
        errors, data_page, TopMenuSelectors.PROJECT_NAME.value,
        help_text=NOT_CLICKABLE_MESSAGE.format(
            TAKE_TO_NEXT_LEVEL_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 27. Assert workers can be decreased while
    #     'Let's take this to the next level' tooltip is present.
    # --------------------------------------------------------------------
    assert_workers_can_be_decreased(errors)

    # --------------------------------------------------------------------
    # 28. Assert content of 'Let's take this to the next level' tooltip
    # --------------------------------------------------------------------
    go_to_next_tour_slide(
        BuildModelsTooltipSelectors.MODELS_CAN_RUN_TITLE.value)
    assert_tooltip_multi_content(
        errors, MODELS_CAN_RUN_TOOLTIP_TITLE, MODELS_CAN_RUN_TOOLTIP_CONTENT,
        check_back_button=True)

    # --------------------------------------------------------------------
    # 29. Assert 'Models' tab is highlighted while
    #     MODELS CAN RUN, BUT THEY CAN'T HIDE tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_highlighted_by_pendo(
        errors, data_page, TopMenuSelectors.MODELS_TAB.value,
        NOT_HIGHLIGHTED_MESSAGE.format(MODELS_CAN_RUN_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 30. Assert MLOps tab at the top of the page is not clickable
    #     while MODELS CAN RUN, BUT THEY CAN'T HIDE tooltip is present
    # --------------------------------------------------------------------
    assert_element_is_not_clickable(
        errors, data_page, TopMenuSelectors.DEPLOYMENTS_TAB.value,
        help_text=NOT_CLICKABLE_MESSAGE.format(MODELS_CAN_RUN_TOOLTIP_TITLE))

    # --------------------------------------------------------------------
    # 31. User can proceed to Models tab while
    #     MODELS CAN RUN, BUT THEY CAN'T HIDE tooltip is present
    # --------------------------------------------------------------------
    top_menu_page.go_to_top_menu_page(
        top_menu_page.models_tab, TopMenuSelectors.MODELS_TAB.value,
        close_pendo_tour=False)

    # --------------------------------------------------------------------
    # 32. Assert content of last tooltip
    # --------------------------------------------------------------------
    assert_tooltip_multi_content(
        errors, LAST_TOOLTIP_TITLE, LAST_TOOLTIP_CONTENT,
        check_back_button=False)

    # --------------------------------------------------------------------
    # 33. Assert Was this tour helpful? section of last tooltip
    # --------------------------------------------------------------------
    assert_was_tour_helpful_section(errors)

    models_page.close_pendo_tour_if_present()  # close Deploy Models tour
    tours_guide_component.open_tours_guide()
    tours_guide_component.open_onboarding_tours()
    # --------------------------------------------------------------------
    # 34. Assert tour progress 100%
    # --------------------------------------------------------------------
    # TODO: expected_progress=100% once SELF-2696 is fixed
    # assert_tour_progress(
    #     errors, expected_progress=100, help_text='Tour final progress')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


NOT_CLICKABLE_MESSAGE = 'Must not be clickable while {} tooltip is present.'
NOT_HIGHLIGHTED_MESSAGE = 'Must be highlighted while {} tooltip is present.'


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
    5. Closes Pendo Home tour if present
    """
    def setup_and_sign_in_user(
            credits_amount=20000,
            role=AiProfilePageSelectors.DEVELOPER.value,
            industry=AiProfilePageSelectors.GAMING.value,
            learning_track=AiProfilePageSelectors.CREATE_MODELS.value):

        app_client, _, username, _, _ = payg_drap_user_setup_teardown

        if Envs.STAGING.value in env_params[0]:
            app_client.v2_add_feature_flag(
                FeatureFlags.ENABLE_PLATFORM_QUESTIONNAIRE.value
            )
        grant_credits(credits_amount)

        sign_in_user(username)
        create_ai_profile(role, industry, learning_track)

        home_page.close_pendo_tour_if_present()

    return setup_and_sign_in_user


@fixture
def assert_can_view_data_quality_info(data_page):
    """
    Asserts user can view Data Quality Assessment Info
    while 'Tell me more about the data' tooltip is present.
    """
    def can_view_data_quality_info(errors_list):

        if not data_page.view_data_quality_info(raise_error=False):
            errors_list.append(
                f'Could not view Data Quality Assessment Info while "'
                f'{TELL_MORE_ABOUT_DATA_TOOLTIP_TITLE}" tooltip is present.')

    return can_view_data_quality_info


@fixture
def assert_workers_can_be_decreased(modeling_right_sidebar):
    """
    Assert workers can be decreased while 'Let's take this to the next level'
    tooltip is present.
    """
    def workers_can_be_decreased(errors_list):

        if not modeling_right_sidebar.decrease_workers():
            errors_list.append(
                f'Could not decrease workers while '
                f'{TAKE_TO_NEXT_LEVEL_TOOLTIP_TITLE} tooltip is present')

    return workers_can_be_decreased


class BuildModelsTooltipSelectors(Enum):
    # Start page
    START_PAGE_TITLE = TEXT.format('Ready to build AI models fast?')
    START_PAGE_TEXT1 = TEXT.format(
        'This tour will show you just how fast it is to go from importing '
        'data to building predictive models. We will even throw in a peek '
        'at the preparation and insights DataRobot provides along the way.')
    START_PAGE_TEXT2 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Click ")'
    START_PAGE_TEXT3 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Start tour")'
    START_PAGE_TEXT4 = TEXT.format(" and let's do this!")

    # LET'S GET THE DATA
    LETS_GET_DATA_TEXT1 = TEXT.format(
        'With DataRobot, you can start projects using data from:')
    LETS_GET_DATA_TEXT2 = TEXT.format(
        'a local file, URL, or a connected database')
    LETS_GET_DATA_TEXT3 = TEXT.format(
        'data provided with a DataRobot use case')

    # READY, SET, IMPORT!
    READY_SET_IMPORT_TITLE = TEXT.format('Ready, set, import!')
    READY_SET_IMPORT_TEXT1 = TEXT.format(
        'For this tour, we will use the dataset from the ')
    READY_SET_IMPORT_TEXT2 = TEXT.format(
        'Predict Whether a Shipment Will Be Late')
    READY_SET_IMPORT_TEXT3 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                             f':has-text("use case.")'
    READY_SET_IMPORT_TEXT4 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                             f':has-text("Select ")'
    READY_SET_IMPORT_TEXT5 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                             f':has-text("Import dataset")'
    READY_SET_IMPORT_TEXT6 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                             f':has-text(" to continue.")'

    # DATA ANALYSIS IN A FLASH
    DATA_ANALYSIS_TITLE = TEXT.format('data analysis in a flash')
    DATA_ANALYSIS_TEXT1 = TEXT.format(
        'Follow along in the right panel as DataRobot uploads the data, '
        'analyzes it, and summarizes the main characteristics. This is known'
        ' as “Exploratory Data Analysis” (EDA).')
    DATA_ANALYSIS_TEXT2 = TEXT.format('EDA consists of:')
    DATA_ANALYSIS_TEXT3 = TEXT.format('counting and categorizing')
    DATA_ANALYSIS_TEXT4 = TEXT.format(
        'applying automatic feature transformations (where appropriate)')
    DATA_ANALYSIS_TEXT5 = TEXT.format(
        'A process that can take hours (or even days!), '
        'DataRobot does in seconds.')

    # VISUALIZE THE FEATURE DETAILS
    FEATURE_DETAILS_TITLE = TEXT.format('Visualize the feature details')
    FEATURE_DETAILS_TEXT1 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                            f':has-text("Click on ")'
    FEATURE_DETAILS_TEXT2 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Vendor")'
    FEATURE_DETAILS_TEXT3 = TEXT.format(
        ' from the list of features. A feature is a column from the dataset.')
    FEATURE_DETAILS_TEXT4 = TEXT.format(
        'Depending on feature type, you can see histograms, frequent value'
        ' types, and more. ')
    FEATURE_DETAILS_TEXT5 = TEXT.format(
        'If transformations have been applied, they are also listed. ')

    # TELL ME MORE ABOUT THE DATA
    TELL_MORE_ABOUT_DATA_TITLE = TEXT.format('Tell me more about the data')
    TELL_MORE_ABOUT_DATA_TEXT1 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                                 f':has-text("Click on ")'
    TELL_MORE_ABOUT_DATA_TEXT2 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                                 f':has-text("View info")'
    TELL_MORE_ABOUT_DATA_TEXT3 = TEXT.format(' to see how the dataset fared. ')
    TELL_MORE_ABOUT_DATA_TEXT4 = TEXT.format(
        'The data quality assessment detects common data quality issues, '
        'marking those features in the data table for easy identification. ')
    TELL_MORE_ABOUT_DATA_TEXT5 = TEXT.format(
        'DataRobot fixes issues where it can, providing a report of the '
        'automated processing it applied. ')

    # WHAT WOULD YOU LIKE TO PREDICT?
    WHAT_TO_PREDICT_TITLE = TEXT.format('What would you like to predict?')
    WHAT_TO_PREDICT_TEXT1 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Enter ")'
    WHAT_TO_PREDICT_TEXT2 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                            f':has-text("Late_delivery")'
    WHAT_TO_PREDICT_TEXT3 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                            f':has-text(" as the target. ")'
    WHAT_TO_PREDICT_TEXT4 = TEXT.format(
        'The target feature is the name of the column in the dataset that '
        'you would like to predict.')
    WHAT_TO_PREDICT_TEXT5 = TEXT.format('Take notice of:')
    WHAT_TO_PREDICT_TEXT6 = TEXT.format(
        'The histogram that appears after you enter the target. '
        'This shows you the distribution of the target values. ')
    WHAT_TO_PREDICT_TEXT7 = TEXT.format(
        'The type of project that will be built. This use case is'
        ' ‘Classification’, but you can also build regression, multiclass, '
        'multilabel, and unsupervised projects.')

    # Ready to model?
    READY_TO_MODEL_TITLE = TEXT.format('ready to model?')
    READY_TO_MODEL_TEXT1 = TEXT.format(
        'This is the moment you\'ve been waiting for...')
    READY_TO_MODEL_TEXT2 = TEXT.format(
        'You\'ve loaded the data, reviewed the EDA '
        '(Exploratory Data Analysis), and selected the target to predict. ')
    READY_TO_MODEL_TEXT3 = TEXT.format(
        'Now, there is only one thing standing between you and your '
        'AI models.')
    READY_TO_MODEL_TEXT4 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Click ")'
    READY_TO_MODEL_TEXT5 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Start")'
    READY_TO_MODEL_TEXT6 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                           f':has-text(" to begin building!")'

    # Whats happening behind the curtain?
    BEHIND_CURTAIN_TITLE = TEXT.format('whats happening behind the curtain?')
    BEHIND_CURTAIN_TEXT1 = TEXT.format('After you click start:')
    BEHIND_CURTAIN_TEXT2 = TEXT.format('Models begin building. ')
    BEHIND_CURTAIN_TEXT3 = TEXT.format(
        '(Watch progress bar in the right pane.)')
    BEHIND_CURTAIN_TEXT4 = TEXT.format(
        'Based on the target feature, DataRobot will train on a predefined '
        'set of models and sample sizes.')

    # Let's take this to the next level
    TAKE_TO_NEXT_LEVEL_TITLE = TEXT.format(
        'Let\'s take this to the next level')
    TAKE_TO_NEXT_LEVEL_TEXT1 = TEXT.format(
        'Check to see if you can boost workers by clicking on the ')
    TAKE_TO_NEXT_LEVEL_TEXT2 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                               f':has-text("up arrow")'
    TAKE_TO_NEXT_LEVEL_TEXT3 = TEXT.format(
        'More workers increases the speed of model building by dedicating '
        'more compute power to your project. '
        'Building in parallel means more models in less time. Hooray!')

    # Models can run, but they can't hide
    MODELS_CAN_RUN_TITLE = TEXT.format('models can run, but they can\'t hide')
    MODELS_CAN_RUN_TEXT1 = TEXT.format(
        ' is the place to see and access the models DataRobot built. '
        'It populates throughout the build process, with an ever-updating ')
    MODELS_CAN_RUN_TEXT2 = TEXT.format('badge number')
    MODELS_CAN_RUN_TEXT3 = TEXT.format(' showing the current model count.')
    MODELS_CAN_RUN_TEXT4 = TEXT.format(
        'You can see the Leaderboard and the models being built in real-time '
        'by clicking into the ')
    MODELS_CAN_RUN_TEXT5 = TEXT.format('When you are ready, click on ')

    # Well done—and ahead of deadline too!
    LAST_PAGE_TITLE = TEXT.format('Well done — and ahead of deadline too! ')
    LAST_PAGE_TEXT1 = TEXT.format(
        'Soak it in... DataRobot is building 20-30 different models, '
        'using a “survival of the fittest” strategy to find the most '
        'accurate model and prepare it for deployment. ')
    LAST_PAGE_TEXT2 = TEXT.format(
        'In what would take hours or days to hand-code, '
        'DataRobot will complete in under 20 minutes. ')
    LAST_PAGE_TEXT3 = TEXT.format('While your models run, feel free to '
                                  'step away and:')
    LAST_PAGE_TEXT4 = TEXT.format('take your dog for a walk')
    LAST_PAGE_TEXT5 = TEXT.format('grab a coworker for a coffeebreak')
    LAST_PAGE_TEXT6 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                      f':has-text("listen to this ")'
    LAST_PAGE_TEXT7 =\
        f'{TOOLTIP_TEXT_CLASS_VALUE}' \
        f' [href="https://www.datarobot.com/ai-heroes/podcasts/' \
        f'shiny-ai-toys-on-real-world-problems/"]'
    LAST_PAGE_TEXT8 = TEXT.format(
        'Whenever you\'re ready, the Leaderboard of models will be waiting '
        'for you to explore. Be sure to take a moment, celebrate, and think '
        'about how much you\'ve accomplished. ')
    LAST_PAGE_TEXT9 = TEXT.format('Lastly, how else can we help?')
    LAST_PAGE_TEXT10 = f'{TOOLTIP_TEXT_CLASS_VALUE} :has-text("Join the ")'
    LAST_PAGE_TEXT11 = f'{TOOLTIP_TEXT_CLASS_VALUE} ' \
                       f'[href="https://community.datarobot.com"]'
    LAST_PAGE_TEXT12 = TEXT.format(
        ' for fast, easy support. (Heck, join it even if you don\'t need '
        'help. We really like you.)')
    LAST_PAGE_TEXT13 = ':has-text(' \
                       '"Want to keep learning? Give your leaderboard a ' \
                       'chance to populate with a list of models then:")'
    # LAST_PAGE_TEXT14 = TEXT.format('Launch the Explore AI Models Tour!')
    LAST_PAGE_TEXT14 = TEXT.format(
        'Launch a tour to learn how to deploy a model')


START_PAGE_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.START_PAGE_TITLE.value,
            BuildModelsTooltipSelectors.START_PAGE_TEXT1.value,
            BuildModelsTooltipSelectors.START_PAGE_TEXT2.value,
            BuildModelsTooltipSelectors.START_PAGE_TEXT3.value,
            BuildModelsTooltipSelectors.START_PAGE_TEXT4.value,
        ]
LETS_GET_DATA_TOOLTIP_TITLE = 'Let\'s get the data'
LETS_GET_DATA_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.LETS_GET_DATA_TEXT1.value,
            BuildModelsTooltipSelectors.LETS_GET_DATA_TEXT2.value,
            BuildModelsTooltipSelectors.LETS_GET_DATA_TEXT3.value,
        ]
READY_SET_IMPORT_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TEXT1.value,
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TEXT2.value,
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TEXT3.value,
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TEXT4.value,
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TEXT5.value,
            BuildModelsTooltipSelectors.READY_SET_IMPORT_TEXT6.value
        ]
DATA_ANALYSIS_TOOLTIP_TITLE = 'Data analysis in a flash'
DATA_ANALYSIS_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.DATA_ANALYSIS_TEXT1.value,
            BuildModelsTooltipSelectors.DATA_ANALYSIS_TEXT2.value,
            BuildModelsTooltipSelectors.DATA_ANALYSIS_TEXT3.value,
            BuildModelsTooltipSelectors.DATA_ANALYSIS_TEXT4.value,
            BuildModelsTooltipSelectors.DATA_ANALYSIS_TEXT5.value
        ]
FEATURE_DETAILS_TOOLTIP_TITLE = 'Visualize the feature details'
FEATURE_DETAILS_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.FEATURE_DETAILS_TEXT1.value,
            BuildModelsTooltipSelectors.FEATURE_DETAILS_TEXT2.value,
            BuildModelsTooltipSelectors.FEATURE_DETAILS_TEXT3.value,
            BuildModelsTooltipSelectors.FEATURE_DETAILS_TEXT4.value,
            BuildModelsTooltipSelectors.FEATURE_DETAILS_TEXT5.value
        ]
TELL_MORE_ABOUT_DATA_TOOLTIP_TITLE = 'Tell me more about the data'
TELL_MORE_ABOUT_DATA_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.TELL_MORE_ABOUT_DATA_TEXT1.value,
            BuildModelsTooltipSelectors.TELL_MORE_ABOUT_DATA_TEXT2.value,
            BuildModelsTooltipSelectors.TELL_MORE_ABOUT_DATA_TEXT3.value,
            BuildModelsTooltipSelectors.TELL_MORE_ABOUT_DATA_TEXT4.value,
            BuildModelsTooltipSelectors.TELL_MORE_ABOUT_DATA_TEXT5.value
        ]
WHAT_TO_PREDICT_TOOLTIP_TITLE = 'What would you like to predict?'
WHAT_TO_PREDICT_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT1.value,
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT2.value,
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT3.value,
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT4.value,
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT5.value,
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT6.value,
            BuildModelsTooltipSelectors.WHAT_TO_PREDICT_TEXT7.value,
        ]
READY_TO_MODEL_TOOLTIP_TITLE = 'Ready to model?'
READY_TO_MODEL_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.READY_TO_MODEL_TEXT1.value,
            BuildModelsTooltipSelectors.READY_TO_MODEL_TEXT2.value,
            BuildModelsTooltipSelectors.READY_TO_MODEL_TEXT3.value,
            BuildModelsTooltipSelectors.READY_TO_MODEL_TEXT4.value,
            BuildModelsTooltipSelectors.READY_TO_MODEL_TEXT5.value,
            BuildModelsTooltipSelectors.READY_TO_MODEL_TEXT6.value,
        ]
BEHIND_CURTAIN_TOOLTIP_TITLE = 'whats happening behind the curtain?'
BEHIND_CURTAIN_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.BEHIND_CURTAIN_TEXT1.value,
            BuildModelsTooltipSelectors.BEHIND_CURTAIN_TEXT2.value,
            BuildModelsTooltipSelectors.BEHIND_CURTAIN_TEXT3.value,
            BuildModelsTooltipSelectors.BEHIND_CURTAIN_TEXT4.value,
        ]
TAKE_TO_NEXT_LEVEL_TOOLTIP_TITLE = 'Let\'s take this to the next level'
TAKE_TO_NEXT_LEVEL_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.TAKE_TO_NEXT_LEVEL_TEXT1.value,
            BuildModelsTooltipSelectors.TAKE_TO_NEXT_LEVEL_TEXT2.value,
            BuildModelsTooltipSelectors.TAKE_TO_NEXT_LEVEL_TEXT3.value,
        ]
MODELS_CAN_RUN_TOOLTIP_TITLE = 'models can run, but they can\'t hide'
MODELS_CAN_RUN_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.MODELS_CAN_RUN_TEXT1.value,
            BuildModelsTooltipSelectors.MODELS_CAN_RUN_TEXT2.value,
            BuildModelsTooltipSelectors.MODELS_CAN_RUN_TEXT3.value,
            BuildModelsTooltipSelectors.MODELS_CAN_RUN_TEXT4.value,
            BuildModelsTooltipSelectors.MODELS_CAN_RUN_TEXT5.value,
        ]
LAST_TOOLTIP_TITLE = 'Well done—and ahead of deadline too!'
LAST_TOOLTIP_CONTENT = [
            BuildModelsTooltipSelectors.LAST_PAGE_TITLE.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT1.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT2.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT3.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT4.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT5.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT6.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT7.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT8.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT9.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT10.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT11.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT12.value,
            BuildModelsTooltipSelectors.LAST_PAGE_TEXT13.value,
            # BuildModelsTooltipSelectors.LAST_PAGE_TEXT14.value,
        ]
