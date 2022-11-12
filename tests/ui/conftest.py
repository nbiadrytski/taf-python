import logging
from time import sleep
from os import environ

from pytest import fixture

from pages import *
from utils.http_utils import Request
from utils.selectors_enums import (
    PendoTourSelectors,
    AiProfilePageSelectors,
    HomePageSelectors,
    DrapUsagePageSelectors
)
from utils.data_enums import (
    EnvVars,
    HtmlAttribute,
    Envs
)
from utils.ui_constants import (
    ELEMENT_FOUND_MESSAGE,
    ELEMENT_NOT_FOUND_MESSAGE,
    CARD_IS_SELECTED_VALUE,
    ATTR_VALUE_NOT_CONTAINS_MESSAGE,
    ATTR_VALUE_NOT_EQUALS_MESSAGE,
    PENDO_HOME_TOUR_GUIDE_ID,
    PENDO_TOUR_CONTAINER_TIMEOUT,
    ATTR_VALUE_EQUALS_INFO_LOG_MESSAGE,
    ATTR_VALUE_NOT_EQUALS_WARN_LOG_MESSAGE,
    INNER_TEXT_NOT_EQUALS_MESSAGE,
    INNER_TEXT_NOT_EQUALS_LOG_MESSAGE,
    PENDO_HIGHLIGHT
)
from utils.errors import (
    TourNotResetException,
    ElementIsPresentException,
    ElementIsAbsentException,
    ElementIsClickableException,
    ElementIsHiddenException,
    ElementIsVisibleException
)


LOGGER = logging.getLogger(__name__)


@fixture
def browser_context_args(browser_context_args):
    """This fixture is required for tests where files are downloaded"""

    return {
        **browser_context_args,
        'accept_downloads': True
    }


@fixture
def base_page(page, env_params):
    return BasePage(page, env_params)


@fixture
def sign_in_page(page, env_params):
    return SignInPage(page, env_params)


@fixture
def home_page(page, env_params):
    return AiPlatformHomePage(page, env_params)


@fixture
def credits_packs_page(page, env_params):
    return CreditsPacksPage(page, env_params)


@fixture
def invoice_card_page(page, env_params):
    return InvoiceCardPage(page, env_params)


@fixture
def pendo_tour_page(page, env_params):
    return PendoTourPage(page, env_params)


@fixture
def new_page(page, env_params):
    return NewPage(page, env_params)


@fixture
def ai_profile_page(page, env_params):
    return AiProfilePage(page, env_params)


@fixture
def data_page(page, env_params):
    return DataPage(page, env_params)


@fixture
def top_menu_page(page, env_params):
    return TopMenuPage(page, env_params)


@fixture
def modeling_right_sidebar(page, env_params):
    return ModelingRightSidebar(page, env_params)


@fixture
def models_page(page, env_params):
    return ModelsPage(page, env_params)


@fixture
def deployments_page(page, env_params):
    return DeploymentsPage(page, env_params)


@fixture
def apps_page(page, env_params):
    return AppsPage(page, env_params)


@fixture
def tours_guide_component(page, env_params):
    return ToursGuideComponent(page, env_params)


@fixture
def contact_sales_dialog(page, env_params):
    return ContactSalesDialog(page, env_params)


@fixture
def drap_usage_page(page, env_params):
    return DrapUsagePage(page, env_params)


@fixture
def docs_file_types_page(page, env_params):
    return DocsFileTypesPage(page, env_params)


@fixture
def paxata_login_page(page, env_params):
    return PaxataLoginPage(page, env_params)


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
    2. Adds a dict of feature flags optionally
    3. Grants credits to the user
    4. Signs in user
    5. If staging, redirects user to Home page
    6. If prod, creates AI profile
    7. If close_home_tour=True, closes Pendo Home tour if present
    """
    def setup_and_sign_in_user(
            credits_amount=20000,
            role=AiProfilePageSelectors.DEVELOPER.value,
            industry=AiProfilePageSelectors.GAMING.value,
            learning_track=AiProfilePageSelectors.CREATE_MODELS.value,
            add_flags=False,
            flags_dict=None,
            close_home_tour=True):

        app_client, user_id, username, \
        first_name, last_name = payg_drap_user_setup_teardown

        if add_flags:
            app_client.v2_add_feature_flags(flags_dict)

        grant_credits(credits_amount)

        sign_in_user(username)
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
def reset_pendo_tour(status_code, resp_text):
    """
    Resets Pendo tour via Pendo API.
    User needs to refresh the page to see the tour again.
    """
    def reset_tour(user_id, guide_id=PENDO_HOME_TOUR_GUIDE_ID):

        resp = Request('https://app.pendo.io').post_request(
            path=f'api/v1/guide/{guide_id}/visitor/{user_id}/reset',
            headers={
                'x-pendo-integration-key': environ[EnvVars.PENDO_INTEGRATION_KEY.value]
            })
        status = status_code(resp)

        assert status == 200, \
            f'Tour {guide_id} for userId {user_id} was not reset' \
            f'. Status code: {status}. Resp: {resp_text(resp)}'
        LOGGER.debug(
            'Tour %s reset request for user %s passed', guide_id, user_id)

    return reset_tour


@fixture
def confirm_pendo_tour_is_reset(reset_pendo_tour,
                                pendo_tour_page):
    """
    Make sure Pendo tour is reset:
    1. Close tour container if present
    2. Reset tour so that it appears at start page
    3. Refresh the page
    Perform the above 3 steps until
    reset_round >= max expected rounds,
    If True -> raises TourNotResetException
    """
    def confirm_tour_is_reset(current_page, user_id, rounds_max=5, poll_interval=1):

        reset_round = 0
        while True:
            reset_round = reset_round + 1

            if current_page.is_element_present(
                    PendoTourSelectors.TOUR_CONTAINER.value,
                    timeout=PENDO_TOUR_CONTAINER_TIMEOUT, screenshot=False, raise_error=False
            ):  # close tour if present
                current_page.click_element(pendo_tour_page.close_tour_x_button)
                LOGGER.info('Closed pendo tour. Round %d', reset_round)

            reset_pendo_tour(user_id)
            current_page.refresh_page()
            LOGGER.info('Waiting for tour container. Round %d', reset_round)

            if reset_round >= rounds_max:
                current_page.make_screenshot(PendoTourSelectors.TOUR_CONTAINER.value)
                LOGGER.error('Tour was not reset. Round %s ', reset_round)
                raise TourNotResetException(user_id, reset_round)

            if current_page.is_element_present(
                    PendoTourSelectors.TOUR_CONTAINER.value,
                    timeout=PENDO_TOUR_CONTAINER_TIMEOUT, screenshot=False, raise_error=False
            ):  # tour is present if tour container elem is present
                LOGGER.info('Tour is reset. Round %d', reset_round)
                break

            sleep(poll_interval)

    return confirm_tour_is_reset


@fixture
def assert_pendo_tour_is_absent():
    """
    If Pendo tour container element is present at the page,
    either adds error message to errors_list (if add_to_errors=True)
    or raises ElementIsPresentException (if raise_error=True),
    otherwise logs a message.
    """
    def assert_pendo_tour_is_absent(current_page, errors_list, help_text='',
                                    add_to_errors=True, raise_error=False):

        if current_page.is_element_present(
                PendoTourSelectors.TOUR_CONTAINER.value,
                timeout=PENDO_TOUR_CONTAINER_TIMEOUT,
                screenshot=False, raise_error=False
        ):
            if add_to_errors:
                errors_list.append(
                    ELEMENT_FOUND_MESSAGE.format(
                        PendoTourSelectors.TOUR_CONTAINER.value, help_text))
            else:
                if raise_error:
                    current_page.make_screenshot(PendoTourSelectors.TOUR_CONTAINER.value)
                    raise ElementIsPresentException(PendoTourSelectors.TOUR_CONTAINER.value)

                LOGGER.warning('Pendo tour is unexpectedly present')
        else:
            LOGGER.info('Pendo tour is expectedly absent')

    return assert_pendo_tour_is_absent


@fixture
def assert_no_tour_again_if_closed(assert_pendo_tour_is_absent,
                                   confirm_pendo_tour_is_reset):
    """
    Closes Pendo tour by clicking button_element
    (it can be X, Remind me tomorrow, No thanks button, etc.)
    Asserts the tour is absent.
    Refreshes the page and asserts the tour is still absent.
    """
    def assert_tour_not_appears_again(current_page, button_element,
                                      errors_list, help_text=''):
        # Close tour
        current_page.click_element(button_element)
        # Tour should be closed now
        assert_pendo_tour_is_absent(current_page, errors_list, help_text)

        current_page.refresh_page()
        # Tour doesn't appear again
        assert_pendo_tour_is_absent(current_page, errors_list, help_text)

    return assert_tour_not_appears_again


@fixture
def assert_tour_back_close_buttons_present(pendo_tour_page):
    """Assert tooltip Back and Close (X) buttons are present"""

    def back_and_close_buttons_are_present(errors_list, help_text=''):

        # Assert Back button is present
        if not pendo_tour_page.is_element_present(PendoTourSelectors.BACK_BUTTON.value):
            errors_list.append(
                ELEMENT_NOT_FOUND_MESSAGE.format(
                    PendoTourSelectors.BACK_BUTTON.value, help_text))
        # Assert Close(X) button is present
        if not pendo_tour_page.is_element_present(PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value):
            errors_list.append(
                ELEMENT_NOT_FOUND_MESSAGE.format(
                    PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value, help_text))

    return back_and_close_buttons_are_present


@fixture
def assert_tooltip_content(pendo_tour_page, assert_element_is_present,
                           assert_tour_back_close_buttons_present):
    """
    Start tour (or go to next tooltip) and check its title and text below title.
    Assert Back and close (X) buttons are present.
    """
    def assert_tooltip_content(title_selector, content_selector,
                               errors_list, start_tour=False,
                               check_back_close_buttons=True,
                               check_close_button=False,
                               click_next=True):

        # Either start the tour or click Next button to go to next tooltip
        if start_tour:
            pendo_tour_page.start_tour()
        else:
            if click_next:
                pendo_tour_page.click_next_button()

        # Check tooltip title
        assert_element_is_present(
            pendo_tour_page, title_selector, errors_list,
            f'Check title of {title_selector} tooltip')
        # Check tooltip content
        assert_element_is_present(
            pendo_tour_page, content_selector, errors_list,
            f'Check content of {title_selector} tooltip')
        # Check if Back and Close (X) buttons are present
        if check_back_close_buttons:
            assert_tour_back_close_buttons_present(
                errors_list, f'Check Back and Close buttons at "{title_selector}" tooltip')
        # Check if Close (X) button is present
        if check_close_button:
            if not pendo_tour_page.is_element_present(PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value):
                errors_list.append(ELEMENT_NOT_FOUND_MESSAGE.format(
                    PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value,
                    f'X (close) tour button is absent at {title_selector} tooltip'))

    return assert_tooltip_content


@fixture
def assert_tour_start_page_content(assert_tour_start_page_image,
                                   assert_element_is_present, pendo_tour_page):
    """Asserts image and text content of Pendo tour start page."""

    def start_page_content(errors_list, text_lines_list):

        assert_tour_start_page_image(errors_list)

        for text_line in text_lines_list:
            assert_element_is_present(
                pendo_tour_page, text_line, errors_list, 'Check start page content')

    return start_page_content


@fixture
def go_to_next_tour_slide(pendo_tour_page):
    """Clicks Next button from Pendo tooltip and waits for element with passed selector."""

    def go_to_next_slide(selector_to_wait_for):

        pendo_tour_page.click_next_button()
        pendo_tour_page.wait_for_element(selector_to_wait_for)

    return go_to_next_slide


@fixture
def assert_tooltip_multi_content(assert_element_is_present, pendo_tour_page):
    """
    Validates text content of Pendo tour tooltip with multiple text lines.
    Asserts X (Close) button is present.
    Optionally checks if 'Back' button is present at tooltip.
    """
    def tooltip_multi_content(errors_list, tooltip_title, text_lines_list,
                              check_back_button=False):

        for text_line in text_lines_list:
            assert_element_is_present(
                pendo_tour_page, text_line, errors_list, f'Check content of {tooltip_title} tooltip')
        if not pendo_tour_page.is_element_present(PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value):
            errors_list.append(
                ELEMENT_NOT_FOUND_MESSAGE.format(
                    PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value,
                    f'X (close) tour button is absent at {tooltip_title} tooltip'))
        if check_back_button:
            if not pendo_tour_page.is_element_present(PendoTourSelectors.BACK_BUTTON.value):
                errors_list.append(
                    ELEMENT_NOT_FOUND_MESSAGE.format(
                        PendoTourSelectors.BACK_BUTTON.value,
                        f'"Back" button is absent at {tooltip_title} tooltip'))

    return tooltip_multi_content


@fixture
def close_and_reset_tour(
        assert_pendo_tour_is_absent, confirm_pendo_tour_is_reset
):
    """
    Clicks pendo_tour_page button which can close tour.
    Asserts that the tour container is closed.
    Resets the tour and confirms it's reset.
    """
    def close_and_reset_tour(
            current_page, user_id, button_element, errors_list, help_text=''
    ):
        # Click No thanks button
        current_page.click_element(button_element)
        from time import sleep
        sleep(10)
        # TODO: delete below 5 lines once SELF-2716 is fixed
        if current_page.is_element_present(
                PendoTourSelectors.TOUR_CONTAINER.value, screenshot=False
        ):
            current_page.click_selector(
                PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value)
        # Tour should be closed now
        assert_pendo_tour_is_absent(current_page, errors_list, help_text)
        confirm_pendo_tour_is_reset(current_page, user_id)

    return close_and_reset_tour


@fixture
def sign_in_user(sign_in_page):
    """Navigates to sign in page and signs in a user"""

    def sign_in(username, is_auth0=False):

        sign_in_page.navigate()
        sign_in_page.sign_in(username, is_auth0=is_auth0)

    return sign_in


@fixture
def assert_element_is_present():
    """
    If element is not present at page, adds error message to errors_list (if add_to_errors=True)
    or raises ElementIsAbsentException (if raise_error=True), otherwise logs a message.
    """
    def assert_element_is_present(page, selector, errors_list, help_text='',
                                  add_to_errors=True, raise_error=False):

        if not page.is_element_present(selector):
            if add_to_errors:
                errors_list.append(ELEMENT_NOT_FOUND_MESSAGE.format(selector, help_text))
            else:
                if raise_error:
                    raise ElementIsAbsentException(selector)

                LOGGER.warning('Element with selector %s is not present', selector)

    return assert_element_is_present


@fixture
def assert_element_is_not_present():
    """
    If element is present at page, adds error message to errors_list (if add_to_errors=True)
    or raises ElementIsAbsentException (if raise_error=True), otherwise logs a message.
    """
    def element_is_not_present(page, selector, errors_list, help_text='', add_to_errors=True,
                               raise_error=False):

        if page.is_element_present(selector, timeout=5000, screenshot=False):
            if add_to_errors:
                errors_list.append(ELEMENT_NOT_FOUND_MESSAGE.format(selector, help_text))
            else:
                if raise_error:
                    raise ElementIsAbsentException(selector)

                LOGGER.warning('Element with selector %s is present', selector)

    return element_is_not_present


@fixture
def assert_attribute_value_contains():
    """
    Gets attribute value of element. If expected value is not in actual value,
    either ValueError is raised (if raise_error=True) or a message is logged.
    """
    def assert_attribute_value(current_page, selector, attribute_name,
                               expected_value, errors_list, help_text='',
                               add_to_errors=True, raise_error=False):

        actual_value = current_page.get_attribute_value(selector, attribute_name)
        if expected_value not in actual_value:
            if add_to_errors:
                errors_list.append(
                    ATTR_VALUE_NOT_CONTAINS_MESSAGE.format(
                        attribute_name, actual_value, selector, expected_value, help_text))
            else:
                if raise_error:
                    raise ValueError(f'"{expected_value} is not in "{actual_value}" value of'
                                     f' attribute {attribute_name}')
                LOGGER.warning(
                    '"%s" is not in "%s" value of attribute %s ',
                    expected_value, actual_value, attribute_name)
        else:
            LOGGER.info('"%s" is in "%s" value of attribute %s ',
                        expected_value, actual_value, attribute_name)

    return assert_attribute_value


@fixture
def assert_attribute_value_equals():
    """
    Gets attribute value of element. If expected value != actual value,
    either ValueError is raised (if raise_error=True) or a message is logged.
    """
    def assert_attribute_value(
            current_page, selector, attribute_name, expected_value,
            errors_list, help_text='', add_to_errors=True, raise_error=False):

        actual_value = current_page.get_attribute_value(selector, attribute_name)
        if expected_value != actual_value:
            if add_to_errors:
                errors_list.append(
                    ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                        attribute_name, actual_value, selector, expected_value, help_text))
            else:
                if raise_error:
                    raise ValueError(
                        ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                            attribute_name, actual_value, selector, expected_value, help_text))
                LOGGER.warning(
                    ATTR_VALUE_NOT_EQUALS_WARN_LOG_MESSAGE, actual_value, attribute_name, expected_value)
        else:
            LOGGER.info(
                ATTR_VALUE_EQUALS_INFO_LOG_MESSAGE, actual_value, attribute_name, expected_value)

    return assert_attribute_value


@fixture
def assert_home_page_card_is_selected(home_page):
    """Asserts if Home page card: Data Prep, ML Development, ML Ops is selected"""

    def home_page_card_is_selected(
            card_selector, errors_list, add_to_errors=True, raise_error=False):

        help_text = f'"{card_selector}" card should be selected!'
        actual_attr_value = home_page.get_attribute_value(
            card_selector, HtmlAttribute.CLASS.value
        )
        if CARD_IS_SELECTED_VALUE != actual_attr_value:
            if add_to_errors:
                errors_list.append(
                    ATTR_VALUE_NOT_CONTAINS_MESSAGE.format(
                        HtmlAttribute.CLASS.value, actual_attr_value,
                        card_selector, CARD_IS_SELECTED_VALUE, help_text)
                )
            if raise_error:
                raise ValueError(
                    ATTR_VALUE_NOT_CONTAINS_MESSAGE.format(
                        HtmlAttribute.CLASS.value, actual_attr_value,
                        card_selector, CARD_IS_SELECTED_VALUE, help_text)
                )
            LOGGER.warning(
                'Home page card %s is not selected. Attribute value: %s',
                card_selector, actual_attr_value
            )
            return False

        LOGGER.info(
            'Home page card %s is selected.', card_selector
        )
        return True

    return home_page_card_is_selected


@fixture
def assert_button_is_disabled():
    """
    Checks if element's disabled attribute == ''. If expected_value != actual_value,
    either adds error message to errors_list and returns False or raises ValueError.
    If expected_value == actual_value, returns True.
    """
    def button_is_disabled(
            current_page, selector, errors_list,
            help_text='', add_to_errors=True, raise_error=False):

        expected_value = ''
        actual_value = current_page.get_attribute_value(
            selector, HtmlAttribute.DISABLED.value,
            raise_error=False
        )
        if actual_value != expected_value:
            if add_to_errors:
                errors_list.append(
                    ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                        HtmlAttribute.DISABLED.value, actual_value,
                        selector, expected_value, help_text))
            if raise_error:
                raise ValueError(
                    ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                        HtmlAttribute.DISABLED.value, actual_value,
                        selector, expected_value, help_text)
                )
            LOGGER.warning(
                ATTR_VALUE_NOT_EQUALS_WARN_LOG_MESSAGE, actual_value,
                HtmlAttribute.DISABLED.value, expected_value
            )
            return False

        return True

    return button_is_disabled


@fixture
def assert_inner_text_equals():
    """
    Asserts inner text of element. If expected_text != actual_text,
    either adds error message to errors_list and returns False or raises ValueError.
    If expected_text == actual_text, returns True.
    """
    def assert_balance(
            current_page, selector, expected_text, errors_list,
            help_text='', add_to_errors=True, raise_error=False):

        actual_text = current_page.get_inner_text(selector)

        if expected_text != actual_text:
            if add_to_errors:
                errors_list.append(
                    INNER_TEXT_NOT_EQUALS_MESSAGE.format(
                        actual_text, selector, expected_text, help_text))
            if raise_error:
                raise ValueError(
                    INNER_TEXT_NOT_EQUALS_MESSAGE.format(
                        actual_text, selector, expected_text, help_text)
                )
            LOGGER.warning(
                INNER_TEXT_NOT_EQUALS_LOG_MESSAGE, actual_text,
                selector, expected_text
            )
            return False

        return True

    return assert_balance


@fixture
def create_ai_profile(ai_profile_page):
    """
    Creates profile at ai-profile page:
    1. Selects roles
    2. Selects industry -> Next
    3. Selects learning track -> Start
    """
    def create_ai_profile(
            role_selector, industry_selector, learning_track_element):

        ai_profile_page.select_role(role_selector)
        ai_profile_page.select_industry(industry_selector)
        ai_profile_page.next_to_track_selection()
        ai_profile_page.select_track(learning_track_element)
        ai_profile_page.finish_profile()

    return create_ai_profile


@fixture
def assert_balance_at_home_page(home_page, assert_inner_text_equals):
    """
    Asserts credits balance at Home page in 2 places:
    1. 'You have N AI Platform Credits' at the left
    2. DataRobot Credits Usage dropdown icon at the right
    """
    def balance_at_home_page(balance, errors_list):

        assert_inner_text_equals(
            home_page, HomePageSelectors.YOU_HAVE_N_CREDITS.value,
            balance, errors_list,
            help_text='Wrong "You have N AI Platform Credits" balance.'
        )
        assert_inner_text_equals(
            home_page, HomePageSelectors.CREDITS_USAGE_DROPDOWN_BUTTON.value,
            balance, errors_list,
            help_text='Wrong balance at DR Credits Usage dropdown icon.')

    return balance_at_home_page


@fixture
def get_balance_with_comma_separator(app_client):
    """Gets current balance and updates it from 19998 to 19,998 format."""

    def balance_with_comma_separator():

        balance = app_client.v2_get_current_credit_balance()
        # add , to digit, e.g. 19998 --> 19,998
        formatted_balance = '{:,}'.format(balance)

        return formatted_balance

    return balance_with_comma_separator


@fixture
def assert_drap_usage_page_balance(assert_element_is_present):
    """
    Asserts balance in 'You have {balance} credits now. The current consumption of your credits:'
    text at DRAP /usage page.
    """
    def drap_usage_page_balance(
            errors_list, drap_usage_page, expected_balance):

        assert_element_is_present(
            drap_usage_page,
            DrapUsagePageSelectors.
                YOU_HAVE_N_CREDITS_TEXT.value.format(expected_balance),
            errors_list,
            f'Wrong balance at DRAP /usage page. '
            f'Expected balance: {expected_balance}')

    return drap_usage_page_balance


@fixture
def go_to_drap_from_full_usage_details(home_page, env_params):
    """
    Clicks 'Full Usage Details' link from Credits Usage widget.
    If prod, user is auto-redirected to DRAP /usage page.
    If staging, user is redirected to Auth0 datarobotdev.auth0.com/login page and then signs in.
    Returns new_page which must be a DRAP /usage page.
    """
    def drap_from_full_usage_details(username, is_signed_in=False):

        if Envs.PROD.value in env_params[0]:
            new_page = home_page.click_full_usage_details_link(
                is_signed_in=True)

            return new_page

        new_page = home_page.click_full_usage_details_link(
            is_signed_in=is_signed_in
        )
        if not is_signed_in:
            new_page.auth0_sign_in(username)

        return new_page

    return drap_from_full_usage_details


@fixture
def assert_tour_start_page_image(pendo_tour_page,
                                 assert_attribute_value_contains):
    """Asserts image is present at Pendo tour start page"""

    def tour_start_page_image(errors_list):

        assert_attribute_value_contains(
            pendo_tour_page, PendoTourSelectors.TOUR_START_PAGE_IMAGE.value,
            attribute_name='xlink:href', expected_value='data:image/jpeg;base64,',
            errors_list=errors_list, help_text='Check image at tour start page')

    return tour_start_page_image


@fixture
def assert_tour_progress(tours_guide_component):
    """Asserts Pendo tour progress bar percentage."""

    def tour_progress_and_steps(errors_list, expected_progress, help_text=''):

        progress = tours_guide_component.get_progress_bar_percent()
        if progress != expected_progress:
            errors_list.append(
                f'Expected tour progress: {expected_progress}, '
                f'got: {progress}. {help_text}')

    return tour_progress_and_steps


@fixture
def assert_was_tour_helpful_section(pendo_tour_page, assert_element_is_present):
    """
    Asserts 'Was this tour helpful?' section of last Pendo tooltip:
    'Was this tour helpful?' text, Yes and No buttons.
    """
    def was_tour_helpful_section(
            errors_list,
            help_text='Check content of "Was this tour helpful?" '
                      'section at last tooltip'):

        assert_element_is_present(
            pendo_tour_page, PendoTourSelectors.WAS_TOUR_HELPFUL_TEXT.value,
            errors_list, help_text=help_text
        )
        assert_element_is_present(
            pendo_tour_page, PendoTourSelectors.HELPFUL_YES_BUTTON.value,
            errors_list, help_text=help_text
        )
        assert_element_is_present(
            pendo_tour_page, PendoTourSelectors.HELPFUL_NO_BUTTON.value,
            errors_list, help_text=help_text)

    return was_tour_helpful_section


@fixture
def assert_element_is_hidden():
    """Asserts element is hidden, the opposite of visible."""

    def element_is_hidden(errors_list, page, selector,
                          add_to_errors_list=True, help_text=''):

        if not page.is_element_hidden(selector):
            if not add_to_errors_list:
                raise ElementIsVisibleException(
                    selector, help_text
                )
            errors_list.append(
                f'Element with selector {selector} is visible.'
                f' {help_text}')

    return element_is_hidden


@fixture
def assert_element_is_visible():
    """Asserts element is not hidden (it is visible)."""

    def element_is_not_hidden(
            errors_list, page, selector,
            add_to_errors_list=True, help_text=''):

        if page.is_element_hidden(selector):
            if not add_to_errors_list:
                raise ElementIsHiddenException(
                    selector, help_text
                )
            errors_list.append(
                f'Element with selector {selector} is hidden.'
                f' {help_text}')

    return element_is_not_hidden


@fixture
def assert_element_is_not_clickable():
    """Asserts element cannot be clicked."""

    def is_element_not_clickable(
            errors_list, page, selector, add_to_errors_list=True,
            help_text=''):

        if page.is_element_clickable(selector):
            if not add_to_errors_list:
                raise ElementIsClickableException(
                    selector, help_text
                )
            errors_list.append(
                f'Element with selector {selector} is clickable.'
                f' {help_text}')

    return is_element_not_clickable


@fixture
def assert_element_is_highlighted_by_pendo():
    """Asserts that element is frame-highlighted by Pendo tour."""

    def element_is_highlighted_by_pendo(errors_list, page, selector,
                                        help_text=''):

        class_value = page.get_attribute_value(
            selector, HtmlAttribute.CLASS.value, raise_error=False
        )
        if PENDO_HIGHLIGHT not in class_value:
            errors_list.append(
                f'Element with selector {selector} is not highlighted'
                f' by Pendo. {help_text}')

    return element_is_highlighted_by_pendo


@fixture
def assert_track_has_card_recommended_label(home_page, assert_element_is_present):
    """
    Asserts Home page learning_track_card: HomePageSelectors.ML_DEV_CARD.value or
    HomePageSelectors.ML_OPS_CARD.value or HomePageSelectors.PAXATA_DATA_PREP_CARD.value has Recommended label.
    """
    def track_card_has_recommended_label(errors_list, learning_track_card):

        assert_element_is_present(
            home_page, HomePageSelectors.RECOMMENDED_LABEL.value.format(learning_track_card),
            errors_list, f'{learning_track_card} card must have Recommended label.')

    return track_card_has_recommended_label
