from pages.base_page import BasePage
from utils.selectors_enums import (
    AiProfilePageSelectors,
    TopMenuSelectors
)
from utils.ui_constants import (
    ATTR_VALUE_NOT_EQUALS_MESSAGE,
    ATTR_VALUE_NOT_CONTAINS_MESSAGE,
)
from utils.data_enums import HtmlAttribute


class AiProfilePage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def role_drop_down(self):
        return self.wait_for_element(
            AiProfilePageSelectors.ROLE_DROPDOWN.value)

    @property
    def industry_drop_down(self):
        return self.wait_for_element(
            AiProfilePageSelectors.INDUSTRY_DROPDOWN.value)

    @property
    def next_button(self):
        return self.wait_for_element(
            AiProfilePageSelectors.NEXT_BUTTON.value)

    @property
    def start_button(self):
        return self.wait_for_element(
            AiProfilePageSelectors.START_BUTTON.value)

    @property
    def prepare_data_option(self):
        return self.wait_for_element(
            AiProfilePageSelectors.PREPARE_DATA.value)

    @property
    def explore_insights_option(self):
        return self.wait_for_element(
            AiProfilePageSelectors.EXPLORE_INSIGHTS.value)

    @property
    def create_ai_models_option(self):
        return self.wait_for_element(
            AiProfilePageSelectors.CREATE_MODELS.value)

    @property
    def deploy_monitor_option(self):
        return self.wait_for_element(
            AiProfilePageSelectors.DEPLOY_AND_MONITOR.value)

    @property
    def analyst_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.ANALYST.value)

    @property
    def data_scientist_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.DATA_SCIENTIST.value)

    @property
    def developer_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.DEVELOPER.value)

    @property
    def director_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.DIRECTOR.value)

    @property
    def executive_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.EXECUTIVE.value)

    @property
    def product_manager_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.PRODUCT_MANAGER.value)

    @property
    def other_role(self):
        return self.wait_for_element(
            AiProfilePageSelectors.OTHER.value)

    def select_role(self, selector):
        """
        Selects user role (Analyst, Developer, etc.) from 'Choose your role' dropdown at ai-profile page.
        Asserts role is selected.
        """
        role = selector.replace('text=', '')
        # Expand role drop down
        self.click_element(self.role_drop_down)
        # Wait for your role selector, e.g.:
        # AiProfilePageSelectors.ANALYST.value
        self.wait_for_element(selector)
        # Select the role
        self.click_selector(selector)
        # Assert the role is selected
        self.wait_for_element(
            f'{AiProfilePageSelectors.ROLE_DROPDOWN.value} '
            f':text-is("{role}")'
        )
        self.logger.info('Role %s is selected', role)

    def select_industry(self, selector):
        """
        Selects industry (Airlines, Gaming, etc.) from 'Choose your industry' dropdown at ai-profile page.
        Asserts industry is selected.
        """
        industry = selector.replace('text=', '')
        # Expand industry drop down
        self.click_element(self.industry_drop_down)
        # Wait for your industry selector, e.g.:
        # AiProfilePageSelectors.GAMING.value
        self.wait_for_element(selector)
        # Select the industry
        self.click_selector(selector)
        # Assert the industry is selected
        self.wait_for_element(
            f'{AiProfilePageSelectors.INDUSTRY_DROPDOWN.value} '
            f':text-is("{industry}")'
        )
        self.logger.info('Industry %s is selected', industry)

    def next_to_track_selection(self):
        """
        Checks if Next button at ai-profile page is enabled, clicks it and
        waits for 'How can DataRobot can help you' page is loaded.
        """
        disabled_attribute = self.get_attribute_value(
                AiProfilePageSelectors.NEXT_BUTTON.value,
                HtmlAttribute.DISABLED.value
        )
        if disabled_attribute is None:
            self.click_element(self.next_button)
            self.wait_for_element(
                AiProfilePageSelectors.HOW_DR_CAN_HELP_TEXT.value
            )
            self.logger.info(
                'User is at ai-profile track selection page.'
            )
        else:
            raise ValueError(
                ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                    HtmlAttribute.DISABLED.value,
                    disabled_attribute,
                    AiProfilePageSelectors.NEXT_BUTTON.value,
                    None,
                    'Next button must be enabled to be clicked'))

    def select_track(self, selector):
        """
        Waits for learning track selector to be present at last ai-profile page.
        Selects learning track.
        Raises ValueError if learning track was not selected
        by checking if track selector 'class' attribute contains 'active' string.
        """
        self.wait_for_element(selector)
        self.click_selector(selector)

        expected_value = 'active'
        class_attribute = self.get_attribute_value(
            selector,
            HtmlAttribute.CLASS.value
        )
        if expected_value not in class_attribute:
            raise ValueError(
                ATTR_VALUE_NOT_CONTAINS_MESSAGE.format(
                    HtmlAttribute.CLASS.value,
                    class_attribute,
                    selector,
                    expected_value,
                    'Learning Track was not selected')
            )
        self.logger.info(
            'Selected %s learning track', selector)

    def finish_profile(self):
        """
        Clicks Start button at last ai-profile page if it is enabled.
        Raises ValueError if Start button is disabled by checking it doesn't have 'disabled' attribute.
        """
        disabled_attribute = self.get_attribute_value(
            AiProfilePageSelectors.START_BUTTON.value,
            HtmlAttribute.DISABLED.value
        )
        if disabled_attribute is None:
            self.click_element(self.start_button)
            self.wait_for_element(
                TopMenuSelectors.PROFILE_ICON.value
            )
            self.logger.info('Finished ai-profile creation')
        else:
            raise ValueError(
                ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                    HtmlAttribute.DISABLED.value,
                    disabled_attribute,
                    AiProfilePageSelectors.START_BUTTON.value,
                    None,
                    'Start button must be enabled to be clicked'))
