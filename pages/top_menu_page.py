from time import sleep

from pages.base_page import BasePage
from utils.selectors_enums import (
    TopMenuSelectors,
    HomePageSelectors
)
from utils.helper_funcs import (
    time_left,
    time
)
from utils.data_enums import HtmlAttribute
from utils.errors import ElementAttributeTimeoutException


class TopMenuPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def dr_logo_icon(self):
        return self.wait_for_element(
            TopMenuSelectors.DR_LOGO.value)

    @property
    def models_tab(self):
        return self.wait_for_element(
            TopMenuSelectors.MODELS_TAB.value)

    @property
    def deployments_tab(self):
        return self.wait_for_element(
            TopMenuSelectors.DEPLOYMENTS_TAB.value)

    @property
    def profile_icon(self):
        return self.wait_for_element(
            TopMenuSelectors.DEPLOYMENTS_TAB.value)

    @property
    def profile_and_settings_option(self):
        return self.wait_for_element(
            TopMenuSelectors.PROFILE_AND_SETTINGS_OPTION.value)

    def go_to_models_page(self):
        self.go_to_top_menu_page(
            self.models_tab,
            TopMenuSelectors.MODELS_TAB.value)

    def go_to_deployments_page(self):
        self.go_to_top_menu_page(
            self.deployments_tab,
            TopMenuSelectors.DEPLOYMENTS_TAB.value)

    def go_to_top_menu_page(
            self, page_tab_element, page_tab_selector,
            close_pendo_tour=True, timeout_period=2, poll_interval=2
    ):
        """
        Goes to top menu page by clicking page tab,
        e.g. Models, Deployments, etc.
        Page element should have 'active' in class attribute,
        meaning the page has loaded.
        """
        timeout = time() + 60 * timeout_period
        while True:
            self.click_element(page_tab_element)
            if close_pendo_tour:
                if page_tab_selector == TopMenuSelectors.MODELS_TAB.value:
                    self.close_pendo_tour_if_present()

            class_attribute = self.get_attribute_value(
                page_tab_selector, HtmlAttribute.CLASS.value
            )
            self.logger.info(
                'Polling for top menu page with selector %s to load. '
                'Time left %s', page_tab_selector, time_left(timeout)
            )
            if time() > timeout:
                raise ElementAttributeTimeoutException(
                    HtmlAttribute.CLASS.value, page_tab_selector,
                    f'Expected "active" in attribute. '
                    f'User is not at page with {page_tab_selector} selector'
                )
            # 'class' attribute value contains 'active'
            # if page tab is selected
            if 'active' in class_attribute:
                self.logger.info('User is at top menu page with %s selector',
                                 page_tab_selector)
                break

            sleep(poll_interval)

    def go_to_home_page_by_clicking_dr_logo_icon(self):
        """Goes to Home page by clicking DR logo icon from top left corner."""

        self.click_element(self.dr_logo_icon)
        self.is_element_present(
            HomePageSelectors.HOME_PAGE_TITLE.value, timeout=30000, raise_error=True,
            help_text='User must be at Home page'
        )
        self.logger.info('Redirected to Home page after clicking DR logo icon')
