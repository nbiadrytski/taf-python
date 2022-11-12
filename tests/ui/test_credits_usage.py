from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ASSERT_ERRORS,
    DATASET_88_MB,
    TEN_K_DIABETES_PROJECT_NAME
)
from utils.selectors_enums import (
    HomePageSelectors,
    AiProfilePageSelectors
)
from utils.data_enums import (
    HtmlAttribute,
    CreditsCategory,
    Envs
)
from utils.helper_funcs import user_identity
from utils.constants import PORTAL_ID_KEY


PROJECT = 'project'
CATEGORY = 'category'
CREDIT_USAGE_BY = 'Credit usage by {}'
SEVEN_DAYS = '7'
THIRTY_DAYS = '30'
NINETY_DAYS = '90'


@mark.ui
def test_credits_usage(setup_and_sign_in_payg_user,
                       home_page,
                       validate_widget_initial_state,
                       upload_3_credit_dataset,
                       get_balance_with_comma_separator,
                       assert_home_page_and_widget_balance,
                       assert_widget_date_filtering,
                       setup_10k_diabetes_credits_data,
                       assert_categories_usage_values,
                       assert_diabetes_project_usage_value,
                       assert_date_filtered_project_value,
                       assert_drap_usage_page_balance,
                       go_to_drap_from_full_usage_details):

    _, _, username, _, _ = setup_and_sign_in_payg_user()

    # Assertion errors will be appended to this list
    errors = []

    home_page.open_credit_usage_widget()
    # ---------------------------------------------------------------
    # 1. Validate initial state of Credits Usage Widget
    # ---------------------------------------------------------------
    validate_widget_initial_state(errors)

    upload_3_credit_dataset()
    eda_balance = get_balance_with_comma_separator()

    # ---------------------------------------------------------------
    # 2. Assert balance at Home page and Credits Usage Widget
    #    after a 3-credit dataset has been uploaded
    # ---------------------------------------------------------------
    assert_home_page_and_widget_balance(errors, eda_balance)

    # ---------------------------------------------------------------
    # 3. Filter Date dropdown by Last 30 and 90 days.
    #    Assert default selected filter is 'Last 7 days'
    # ---------------------------------------------------------------
    assert_widget_date_filtering(errors)

    # ---------------------------------------------------------------
    # 4. Filter Usage dropdown by category and get EDA category value
    # ---------------------------------------------------------------
    home_page.filter_by_usage(CATEGORY)
    eda_value = home_page.get_usage_value(CreditsCategory.EDA.value)

    setup_10k_diabetes_credits_data()

    # ---------------------------------------------------------------
    # 5. Filter Usage dropdown by project after 10k_diabetes project
    #    credits data has been prepared.
    #    Get 'Credit usage by project' (total) usage value and
    #    10k_diabetes.csv usage value
    # ---------------------------------------------------------------
    home_page.filter_by_usage(PROJECT)
    diabetes_value, \
    projects_total_value = _get_usage_values_by_project(home_page)

    # ---------------------------------------------------------------
    # 6. Filter Usage dropdown by category again.
    #    Get Credit usage by category (total), Data Processing,
    #    ML Development and MLOps categories usage values
    # ---------------------------------------------------------------
    home_page.filter_by_usage(CATEGORY)
    total_category_value, data_proc_value, \
    ml_dev_value, ml_ops_value = _get_usage_values_by_category(home_page)

    # ---------------------------------------------------------------
    # 7. Assert sum of categories == Credit usage by category (total)
    # ---------------------------------------------------------------
    assert_categories_usage_values(
        errors, data_proc_value, eda_value, ml_dev_value, ml_ops_value,
        total_category_value)

    # ---------------------------------------------------------------
    # 8. Assert sum of Data Processing and ML Development usage
    #    categories values == 10k_diabetes.csv usage value
    # ---------------------------------------------------------------
    assert_diabetes_project_usage_value(
        errors, data_proc_value, ml_dev_value, diabetes_value)

    # ---------------------------------------------------------------
    # 9. Filter by project and then by Last 30 days.
    #    Assert project usage value filtered by a different date
    #    hasn't changed
    # ---------------------------------------------------------------
    home_page.filter_by_usage(PROJECT)
    home_page.filter_by_date(THIRTY_DAYS)
    assert_date_filtered_project_value(errors, THIRTY_DAYS, diabetes_value)
    # ---------------------------------------------------------------
    # 10. Get final balance. Assert it's reflected at Home page and
    #     Credits Usage Widget circle
    # ---------------------------------------------------------------
    final_balance = get_balance_with_comma_separator()
    assert_home_page_and_widget_balance(errors, final_balance)

    # Go to DRAP Usage page
    drap_usage_page = go_to_drap_from_full_usage_details(
        username, is_signed_in=True)

    # ---------------------------------------------------------------
    # 11. Assert final balance at DRAP /usage page
    # ---------------------------------------------------------------
    assert_drap_usage_page_balance(errors, drap_usage_page, final_balance)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def payg_drap_user_setup_teardown(app_client, dr_account_client, auth0_client):

    # Create and sign up PayAsYouGoUser
    username, first_name, last_name = user_identity()

    user_id = app_client.setup_self_service_user(
        username, first_name, last_name, link_dr_account=True)

    # Register DRAP user
    dr_account_client.register_user(username, first_name, last_name)

    payload = {
        PORTAL_ID_KEY: dr_account_client.portal_id,
        'admin': False, 'creditsUser': True
    }
    # Add creditsUser role to DRAP user
    dr_account_client.admin_update_role(payload)

    yield app_client, user_id, username, first_name, last_name

    # Delete PayAsYouGoUser
    app_client.v2_delete_payg_user(user_id)
    # Delete DRAP user
    dr_account_client.delete_user(dr_account_client.portal_id)
    # Delete Auth0 user if prod
    auth0_client.delete_auth0_user(username)


@fixture
def setup_and_sign_in_payg_user(payg_drap_user_setup_teardown,
                                env_params,
                                grant_credits,
                                sign_in_user,
                                new_page, home_page,
                                create_ai_profile):
    """
    Sets up PayAsYouGoUser for UI tests:
    1. Creates PayAsYouGoUser with DRAP account
    2. Grants credits to the user
    3. Signs in user
    4. If staging, redirects user to Home page
    5. If prod, creates AI profile
    6. If close_home_tour=True, closes Pendo Home tour if present
    """
    def setup_and_sign_in_user(
            credits_amount=20000,
            role=AiProfilePageSelectors.DEVELOPER.value,
            industry=AiProfilePageSelectors.GAMING.value,
            learning_track=AiProfilePageSelectors.CREATE_MODELS.value,
            close_home_tour=True):

        app_client, user_id, username, \
        first_name, last_name = payg_drap_user_setup_teardown

        grant_credits(credits_amount)

        sign_in_user(username, is_auth0=True)
        # ENABLE_PLATFORM_QUESTIONNAIRE is False for staging
        # Therefore, user is redirected to /new page after signing in
        # Redirect user to Home page same as default app2 behavior
        if Envs.STAGING.value in env_params[0]:
            new_page.navigate_to_ai_platform_page()
        else:
            # ENABLE_PLATFORM_QUESTIONNAIRE is True for prod
            # User needs to set up ai profile to proceed to the app
            create_ai_profile(role, industry, learning_track)

        if close_home_tour:
            home_page.close_pendo_tour_if_present()

        return app_client, user_id, username, first_name, last_name

    return setup_and_sign_in_user


@fixture
def validate_widget_initial_state(
        home_page, assert_widget_balance, assert_element_is_present,
        assert_attribute_value_equals, env_params):
    """
    1. Asserts balance at widget circle is 20,000
    2. Asserts 'It looks like you haven't used any credits for that period yet' text is present
    3. Asserts Full Usage Details href is correct
    4. Asserts Usage dropdown has By project selected by default
    """
    def widget_initial_state(errors_list):

        assert_widget_balance(errors_list, '20,000')

        message = 'Wrong {} at credits usage widget initial state'
        assert_element_is_present(
            home_page, HomePageSelectors.NO_CREDITS_USED_YET_TEXT.value,
            errors_list, message.format('no credits used text')
        )
        assert_attribute_value_equals(
            home_page, HomePageSelectors.FULL_USAGE_DETAILS_LINK.value,
            HtmlAttribute.HREF.value, f'{env_params[1]}/usage',
            errors_list, message.format('Full Usage Details link')
        )
        assert_element_is_present(
            home_page,
            HomePageSelectors.
                WIDGET_USAGE_DROPDOWN_SELECTED_FILTER.value.format(PROJECT),
            errors_list, message.format(
                '"Usage: By <...>" dropdown default filter selected'))

    return widget_initial_state


@fixture
def assert_widget_balance(home_page):
    """Asserts credits balance at Home page credits widget circle"""

    def widget_balance(errors_list, expected_balance):

        balance = home_page.get_widget_balance()
        if expected_balance != balance:
            errors_list.append(
                f'Expected widget balance: "{expected_balance}", got: "{balance}"')

    return widget_balance


@fixture
def upload_3_credit_dataset(app_client):
    """Upload 88 mb dataset and wait until 3 EDA credits are billed."""

    def upload_dataset():

        app_client.v2_upload_dataset_via_url(DATASET_88_MB)
        app_client.poll_for_balance_range(19997, 19999)

    return upload_dataset


@fixture
def assert_home_page_and_widget_balance(home_page,
                                        assert_balance_at_home_page,
                                        assert_widget_balance):
    """
    1. Waits for expected balance to be in credits line element at Home page
    2. Asserts balance at Home page in 2 places:
        - 'You have N AI Platform Credits' at the left
        - DataRobot Credits Usage dropdown icon at the right
    3. Asserts balance at Usage widget circle
    """

    def home_page_and_widget_balance(errors_list, expected_balance):

        home_page.wait_for_element(
            HomePageSelectors.CREDITS_OVERVIEW_LINE_VALUE.value.format(expected_balance)
        )
        assert_balance_at_home_page(expected_balance, errors_list)
        assert_widget_balance(errors_list, expected_balance)

    return home_page_and_widget_balance


@fixture
def assert_widget_date_filtering(home_page, assert_element_is_present):

    def widget_date_filtering(errors_list):

        message = 'Wrong no credits used text at widget after filtering by {} days'

        date_default_filter = HomePageSelectors.\
            WIDGET_DATE_DROPDOWN_SELECTED_FILTER.value.format(SEVEN_DAYS)
        assert_element_is_present(
            home_page, date_default_filter, errors_list,
            f'Wrong widget Date dropdown filter selected. '
            f'Expected: "{date_default_filter}"'
        )
        home_page.filter_by_date(THIRTY_DAYS)
        assert_element_is_present(
            home_page, HomePageSelectors.NO_CREDITS_USED_YET_TEXT.value,
            errors_list, message.format(THIRTY_DAYS)
        )
        home_page.filter_by_date(NINETY_DAYS)
        assert_element_is_present(
            home_page, HomePageSelectors.NO_CREDITS_USED_YET_TEXT.value,
            errors_list, message.format(NINETY_DAYS))

    return widget_date_filtering


@fixture
def setup_10k_diabetes_credits_data(app_client,
                                    is_credit_category_found):
    """
    Sets up 10k_diabetes project:
    1. Creates a project
    2. Sets a target
    3. Starts modeling in manual mode
    4. Waits until EDA is done
    5. Trains a model
    6. Deploys the model
    7. Waits for MLOps category in GET api/v2/creditsSystem/creditUsageSummary/ resp
    """
    def diabetes_credits_data():

        app_client.setup_10k_diabetes_project()
        is_credit_category_found(CreditsCategory.ML_OPS.value)

    return diabetes_credits_data


@fixture
def assert_categories_usage_values():
    """
    Sums up Data Processing, Exploratory Data Analysis, ML Development, MLOps categories values.
    Asserts the sum of categories == Credit usage by category (total value).
    """
    def categories_usage_values(
            errors_list, data_proc_value, eda_value,
            ml_dev_value, ml_ops_value, total_category_value):

        categories_sum = str(
            int(data_proc_value) + int(eda_value) +
            int(ml_dev_value) + int(ml_ops_value)
        )
        if categories_sum != total_category_value:
            errors_list.append(
                f'Categories sum ({categories_sum}) != '
                f'Credit usage by category ({total_category_value}). '
                f'{CreditsCategory.DATA_PROCESSING.value}: {data_proc_value}.'
                f' {CreditsCategory.EDA.value}: {eda_value}. '
                f'{CreditsCategory.ML_DEV.value}: {ml_dev_value}. '
                f'{CreditsCategory.ML_OPS.value}: {ml_ops_value}.')

    return categories_usage_values


@fixture
def assert_diabetes_project_usage_value():
    """
    Asserts the sum of Data Processing and ML Development usage categories
    == 10k_diabetes.csv usage value
    """
    def diabetes_project_usage_value(
            errors_list, data_proc_value, ml_dev_value, diabetes_value):

        ml_dev_and_data_proc_sum = str(
            int(data_proc_value) + int(ml_dev_value)
        )
        ml_dev_and_data_proc_sum_plus_1 = str(
            int(data_proc_value) + int(ml_dev_value) + 1
        )
        ml_dev_and_data_proc_sum_minus_1 = str(
            int(data_proc_value) + int(ml_dev_value) - 1
        )
        if ml_dev_and_data_proc_sum != diabetes_value and \
                ml_dev_and_data_proc_sum_plus_1 != diabetes_value and \
                ml_dev_and_data_proc_sum_minus_1 != diabetes_value:
            errors_list.append(
                f'Either sum of {CreditsCategory.ML_DEV.value} and '
                f'{CreditsCategory.DATA_PROCESSING.value} '
                f'({ml_dev_and_data_proc_sum}) or sum + 1 '
                f'({ml_dev_and_data_proc_sum_plus_1}) or sum - 1 '
                f'({ml_dev_and_data_proc_sum_minus_1}) != {TEN_K_DIABETES_PROJECT_NAME}'
                f' usage value ({diabetes_value}). '
                f'{CreditsCategory.ML_DEV.value}: {ml_dev_value}. '
                f'{CreditsCategory.DATA_PROCESSING.value}: {data_proc_value}'
            )

    return diabetes_project_usage_value


@fixture
def assert_date_filtered_project_value(home_page):
    """Asserts project usage value filtered by date"""

    def date_filtered_project_value(
            errors_list, days, expected_project_value):

        project_value = home_page.get_usage_value(
            TEN_K_DIABETES_PROJECT_NAME
        )
        if expected_project_value != project_value:
            errors_list.append(
                f'Wrong project value after filtering by {days} days. '
                f'Expected "{expected_project_value}", got "{project_value}"')

    return date_filtered_project_value


def _get_usage_values_by_project(home_page):
    """Returns 10k_diabetes.csv and Credit usage by project (total) usage values."""

    diabetes_value = home_page.get_usage_value(
        TEN_K_DIABETES_PROJECT_NAME
    )
    projects_total_value = home_page.get_usage_value(
        CREDIT_USAGE_BY.format(PROJECT)
    )
    return diabetes_value, projects_total_value


def _get_usage_values_by_category(home_page):
    """
    Returns Credit usage by category (total), Data Processing, ML Development
    and ML Ops categories usage values.
    """
    total_category_value = home_page.get_usage_value(
        CREDIT_USAGE_BY.format(CATEGORY)
    )
    data_proc_value = home_page.get_usage_value(
        CreditsCategory.DATA_PROCESSING.value
    )
    ml_dev_value = home_page.get_usage_value(
        CreditsCategory.ML_DEV.value
    )
    ml_ops_value = home_page.get_usage_value(
        CreditsCategory.ML_OPS.value
    )
    return total_category_value, data_proc_value, \
           ml_dev_value, ml_ops_value
