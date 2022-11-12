from pages.base_page import BasePage
from pages.sign_in_page import SignInPage
from pages.drap_usage_page import DrapUsagePage
from utils.selectors_enums import (
    HomePageSelectors,
    NewPageSelectors,
    CreditsPacksPageSelectors,
    SignInPageSelectors,
    DrapUsagePageSelectors,
    PaxataLoginPageSelectors,
    DeploymentsPageSelectors
)
from utils.data_enums import HtmlAttribute
from utils.ui_constants import CARD_IS_SELECTED_VALUE


MESSAGE = 'redirected to /new page after clicking {} button from ML Dev card'


class AiPlatformHomePage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def buy_credits_button(self):
        return self.wait_for_element(
            HomePageSelectors.BUY_CREDITS.value)

    @property
    def data_prep_card(self):
        return self.wait_for_element(
            HomePageSelectors.PAXATA_DATA_PREP_CARD.value)

    @property
    def data_prep_continue_button(self):
        return self.wait_for_element(
            HomePageSelectors.DATA_PREP_CONTINUE_BUTTON.value)

    @property
    def ml_dev_card(self):
        return self.wait_for_element(
            HomePageSelectors.ML_DEV_CARD.value)

    @property
    def ml_ops_card(self):
        return self.wait_for_element(
            HomePageSelectors.ML_OPS_CARD.value)

    @property
    def go_to_ml_ops_button(self):
        return self.wait_for_element(
            HomePageSelectors.GO_TO_MLOPS_BUTTON.value)

    @property
    def ml_dev_continue_button(self):
        return self.wait_for_element(
            HomePageSelectors.ML_DEV_CONTINUE_BUTTON.value)

    @property
    def ml_dev_create_new_project_button(self):
        return self.wait_for_element(
            HomePageSelectors.CREATE_NEW_PROJECT_BUTTON.value)

    @property
    def credit_usage_dropdown_icon(self):
        return self.wait_for_element(
            HomePageSelectors.CREDITS_USAGE_DROPDOWN_BUTTON.value)

    @property
    def widget_circle(self):
        return self.wait_for_element(
            HomePageSelectors.WIDGET_CIRCLE.value)

    @property
    def widget_date_dropdown(self):
        return self.wait_for_element(
            HomePageSelectors.WIDGET_DATE_DROPDOWN.value)

    @property
    def widget_usage_dropdown(self):
        return self.wait_for_element(
            HomePageSelectors.WIDGET_USAGE_DROPDOWN.value)

    @property
    def full_usage_details_link(self):
        return self.wait_for_element(
            HomePageSelectors.FULL_USAGE_DETAILS_LINK.value)

    def continue_from_ml_dev(self):
        """
        Clicks Continue button from Home page ML Dev card.
        Waits for AI Catalog button to be visible at /new page
        """
        self.click_element(self.ml_dev_continue_button)
        self.wait_for_element(
            NewPageSelectors.AI_CATALOG_BUTTON.value
        )
        self.logger.info(
            'User is at %s page after clicking Continue'
            ' from Home page ML Dev card', self.page_url)

    def go_to_credits_packs_modal(self):
        """Go to Credits Packs modal by clicking Buy Credits button from Home page"""

        self.click_element(self.buy_credits_button)
        self.wait_for_element(
            CreditsPacksPageSelectors.BUY_EXPLORER_PACK_BUTTON.value
        )
        self.logger.info('User went to Credits Packs page')

    def open_credit_usage_widget(self):
        """Opens credit usage widget at Home page"""

        self.click_element(self.credit_usage_dropdown_icon)
        self.wait_for_element(HomePageSelectors.CREDIT_USAGE_WIDGET.value)

    def get_widget_balance(self):
        """Returns balance retrieved from credit usage widget circle"""

        text = self.get_element_inner_text(self.widget_circle)
        balance = text.replace('\n\nDATAROBOT CREDITS', '')
        self.logger.info('Widget balance: %s', balance)

        return balance

    def filter_by_date(self, number_of_days):
        """
        Clicks credit usage widget Date dropdown.
        Selects 'Last N days' option: 7, 30, 90.
        Asserts the option is selected.
        """
        self.click_element(self.widget_date_dropdown)
        self.click_selector(
            HomePageSelectors.LAST_N_DAYS_DROPDOWN_OPTION.value.format(number_of_days)
        )
        self.is_element_present(
            HomePageSelectors.WIDGET_DATE_DROPDOWN_SELECTED_FILTER.value.format(number_of_days),
            raise_error=True)

    def filter_by_usage(self, category):
        """
        Clicks credit usage widget Usage dropdown.
        Selects 'By ...' option (project, category).
        Asserts the option is selected.
        """
        self.click_element(self.widget_usage_dropdown)
        self.click_selector(
            HomePageSelectors.WIDGET_USAGE_DROPDOWN_OPTION.value.format(category)
        )
        self.is_element_present(
            HomePageSelectors.WIDGET_USAGE_DROPDOWN_SELECTED_FILTER.value.format(category),
            raise_error=True)

    def get_usage_value(self, category_name):
        """
        Returns category or project value by its name from Usage dropdown.
        Category name examples:
        ML Development, Data Processing, Credit usage by category (total).
        Project name example: 10k_diabetes.csv, Credit usage by project (total).
        """
        categories = self.get_child_elements_by_selector(
            HomePageSelectors.USAGE_DROPDOWN_CATEGORIES_LIST.value
        )
        for element in categories:
            category_string = element.inner_text()

            if category_name in category_string:
                # get chars after \n which is category value digits
                # e.g. get '3' from 'Exploratory Data Analysis\n3' string
                category_value = category_string.split('\n', 1)[1]
                self.logger.info(
                    '%s value: %s', category_name, category_value
                )
                return category_value

    def click_full_usage_details_link(self, is_signed_in=False):
        """
        Clicks 'Full Usage Details' button from Credits Usage widget.
        Waits for DRAP /usage page to load if user previously signed into DRAP and returns drap_usage_page.
        Waits for Auth0 sign in page to load if user hasn't signed into DRAP before and returns sign_in_page.
        """
        if is_signed_in:
            drap_usage_page = self.open_new_tab(self.full_usage_details_link, DrapUsagePage)
            drap_usage_page.wait_for_element(DrapUsagePageSelectors.USAGE_CONTENT_AREA.value)

            return drap_usage_page
        else:
            sign_in_page = self.open_new_tab(self.full_usage_details_link, SignInPage)
            sign_in_page.wait_for_element(SignInPageSelectors.APP2_GOOGLE_SIGN_IN_BUTTON.value)

            return sign_in_page

    def select_learning_track_card(self, card_element):
        """Selects Home page Learning track card."""

        card = 'learning track card'
        self.click_element(card_element)

        class_value = self.get_element_attribute_value(card_element, HtmlAttribute.CLASS.value)
        if CARD_IS_SELECTED_VALUE != class_value:
            raise ValueError(f'{card_element} {card} was not selected!')

        self.logger.info('Selected %s %s', card_element, card)

    def continue_to_paxata_login_from_data_prep_card(self, paxata_login_page_object):
        """
        Opens Paxata https://k8s-trial.paxata.com/domain/drauth/#/login page in a new tab
        after clicking Continue button from Data Prep card.
        Returns paxata_login_page.
        """
        message = 'Paxata login page after clicking Continue button from Data Prep card'
        paxata_login_page = self.open_new_tab(
            self.data_prep_continue_button, paxata_login_page_object)
        paxata_login_page.wait_for_element(
            PaxataLoginPageSelectors.CONTINUE_BUTTON.value, help_text=f'Could not open {message}'
        )
        self.logger.info('Opened %s', message)

        return paxata_login_page

    def continue_to_new_page_from_ml_dev_card(self):
        """Redirects to /new page after clicking Continue button from ML Dev card."""

        self.click_element(self.ml_dev_continue_button)
        self.wait_for_element(
            NewPageSelectors.DATASETS_REQUIREMENTS_BUTTON.value,
            help_text=f'User was not {MESSAGE.format("Continue")}'
        )
        self.logger.info('User was %s', MESSAGE.format('Continue'))

    def click_create_new_project_button(self):
        """Redirects to /new page after clicking 'Create new project' button from ML Dev card."""

        self.click_element(self.ml_dev_create_new_project_button)
        self.wait_for_element(
            NewPageSelectors.DATASETS_REQUIREMENTS_BUTTON.value,
            help_text=f'User was not {MESSAGE.format("Create new project")}'
        )
        self.logger.info('User was %s', MESSAGE.format('Create new project'))

    def click_go_to_mlops_button(self):
        """Redirects to MLOps page after clicking 'Go to MLOps' button from MLOps track."""

        self.click_element(self.go_to_ml_ops_button)
        self.is_element_present(
            DeploymentsPageSelectors.ACTIVE_DEPLOYMENTS_COUNT.value, timeout=30000,
            raise_error=True, help_text='Must be redirected to MLOps page'
        )
        self.logger.info(
            'Redirected to MLOps page after clicking Go to MLOps button from MLOps track')
