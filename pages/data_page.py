from pages.base_page import BasePage
from utils.selectors_enums import (
    DataPageSelectors,
    ModelingRightSidebar
)
from utils.ui_constants import ATTR_VALUE_NOT_EQUALS_MESSAGE
from utils.errors import ElementIsAbsentException
from utils.helper_funcs import get_id_from_url
from utils.data_enums import HtmlAttribute


class DataPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def recommended_target_button(self):
        # Recommended target is: {RECOMMENDED_TARGET_BUTTON}
        return self.wait_for_element(
            DataPageSelectors.RECOMMENDED_TARGET_BUTTON.value)

    @property
    def target_field(self):
        return self.wait_for_element(
            DataPageSelectors.ENTERED_TARGET.value)

    @property
    def start_modeling_button(self):
        return self.wait_for_element(
            DataPageSelectors.START_MODELING_BUTTON.value)

    @property
    def data_quality_view_info_button(self):
        return self.wait_for_element(
            DataPageSelectors.DATA_QUALITY_VIEW_INFO_BUTTON.value)

    def enter_recommended_target(self, expected_target):
        """
        Sets target by clicking {target_button} from 'Recommended target is: {target_button}'.
        Gets the value of 'value' attribute of entered target element.
        Returns project_id retrieved from page url.
        Raises ValueError if actual_target != expected_target.
        """
        self.click_element(self.recommended_target_button)

        actual_target = self.get_attribute_value(
            DataPageSelectors.ENTERED_TARGET.value, HtmlAttribute.VALUE.value
        )
        if actual_target != expected_target:
            raise ValueError(
                ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                    HtmlAttribute.VALUE.value, actual_target,
                    DataPageSelectors.ENTERED_TARGET.value, expected_target,
                    'Wrong recommended target!')
            )
        project_id = get_id_from_url(self.page_url, index=1)
        self.logger.info(
            'Entered recommended target: %s. Project Id: %s',
            actual_target, project_id
        )
        return project_id

    def enter_target(self, target):
        """
        Enters target into target field.
        Gets the value of 'value' attribute of entered target element.
        Returns project_id retrieved from page url.
        Raises ValueError if actual_target != target.
        """
        self.enter_text(self.target_field, target)

        actual_target = self.get_attribute_value(
            DataPageSelectors.ENTERED_TARGET.value, HtmlAttribute.VALUE.value
        )
        if actual_target != target:
            raise ValueError(
                ATTR_VALUE_NOT_EQUALS_MESSAGE.format(
                    HtmlAttribute.VALUE.value, actual_target,
                    DataPageSelectors.ENTERED_TARGET.value, target, 'Wrong target!')
            )
        project_id = get_id_from_url(self.page_url, index=1)
        self.logger.info(
            'Entered target: %s. Project Id: %s', actual_target, project_id
        )
        return project_id

    def start_modeling(self):
        """
        Clicks Start button element to begin modeling.
        Raises ElementIsAbsentException if 'Setting target feature' selector at the right EDA sidebar
        is not found within timeout (indicating that modeling hasn't started).
        Returns project_id retrieved from projects/{project_id}/eda page url.
        """
        self.click_element(self.start_modeling_button)
        if not self.is_element_present(
                DataPageSelectors.SETTING_TARGET_FEATURE_EDA_STEP.value,
                timeout=100000
        ):
            raise ElementIsAbsentException(
                DataPageSelectors.SETTING_TARGET_FEATURE_EDA_STEP.value,
                'Has Modeling actually started?'
            )
        project_id = get_id_from_url(self.page_url, index=1)
        self.logger.info(
            'Modeling has started. Project Id: %s', project_id
        )
        return project_id

    def wait_for_eda_is_done(self):
        """
        Waits for 'Remove all tasks' button at the right sidebar which indicates EDA has finished.
        Returns project_id retrieved from projects/{project_id}/eda page url.
        """
        self.wait_for_element(
            ModelingRightSidebar.REMOVE_TASKS_BUTTON.value,
            timeout=500000  # ~8.3 minutes
        )
        project_id = get_id_from_url(
            self.page_url, index=1
        )
        self.logger.info(
            'EDA has finished. Project Id: %s', project_id
        )
        return project_id

    def view_data_quality_info(self, raise_error=True):
        """
        Opens Data Quality Assessment Info at projects/{pid}/eda page by clicking 'View info' button.
        If raise_error, raises exception if Data Quality 'Close info' button is not present.
        If not raise_error, returns True if Data Quality 'Close info' button is present.
        Otherwise, returns False.
        """
        data_quality = 'Data Quality Assessment Info.'
        self.click_element(self.data_quality_view_info_button)
        if raise_error:
            self.is_element_present(
                DataPageSelectors.DATA_QUALITY_CLOSE_INFO_BUTTON.value,
                raise_error=True
            )
        if not raise_error:
            if self.is_element_present(
                    DataPageSelectors.DATA_QUALITY_CLOSE_INFO_BUTTON.value
            ):
                self.logger.info('Opened %s', data_quality)
                return True

            self.logger.info('Did not open %s', data_quality)
            return False
