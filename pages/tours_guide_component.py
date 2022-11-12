from time import sleep

from pages.base_page import BasePage
from utils.selectors_enums import (
    ToursGuideSelectors,
    PendoTourSelectors
)
from utils.helper_funcs import get_digits_from_string


class ToursGuideComponent(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def robot_icon(self):
        return self.wait_for_element(
            ToursGuideSelectors.ROBOT_ICON.value)

    @property
    def announcements_button(self):
        # Both Tour Guide menu option and 'back' button
        # to return from ANNOUNCEMENTS to Tour Guide
        return self.wait_for_element(
            ToursGuideSelectors.ANNOUNCEMENTS.value)

    @property
    def onboarding_tours_button(self):
        return self.wait_for_element(
            ToursGuideSelectors.ONBOARDING_TOURS.value)

    @property
    def progress_bar_section(self):
        return self.wait_for_element(
            ToursGuideSelectors.PROGRESS_BAR.value)

    @property
    def build_ai_models_tour(self):
        return self.wait_for_element(
            ToursGuideSelectors.BUILD_AI_MODELS_TOUR.value)

    def get_robot_icon_notifications_count(self):
        """Returns Robot icon badge notifications count."""

        count = self.get_inner_text(
            ToursGuideSelectors.ROBOT_ICON_NOTIFICATION_COUNT.value
        )
        self.logger.info('Robot icon badge notifications count: %s', count)

        return count

    def open_tours_guide(self):
        """Opens Tours guide by clicking Robot icon in bottom left corner."""

        self.click_element(self.robot_icon)
        self.is_element_present(
            ToursGuideSelectors.EXPLORE_DATAROBOT_GUIDE_HEADER.value,
            raise_error=True
        )
        self.logger.info('Opened Tours Guide')

    def open_onboarding_tours(self):
        """Opens Tours Guide Onboarding Tours menu."""

        self.click_element(self.onboarding_tours_button)
        self.is_element_present(
            ToursGuideSelectors.LEFT_ARROW_BUTTON.value, raise_error=True
        )
        self.logger.info('Opened Tours Guide Onboarding Tours')

    def open_tour_from_tours_guide(self, tour_element):
        """
        Clicks tour from Onboarding Tours list.
        Asserts tour is opened by checking Pendo tour container is present.
        """
        self.click_element(tour_element)
        self.is_element_present(
            PendoTourSelectors.TOUR_CONTAINER.value, raise_error=True
        )
        self.logger.info('Opened %s tour', tour_element)

    def get_tour_steps_count(self, tour_selector):
        """
        Returns a tuple of tour current and final steps count retrieved from
        Onboarding Tours list. E.g. (0, 12) from string 'Steps 0 of 12'.
        """
        steps = get_digits_from_string(self.get_inner_text(tour_selector))
        current_step = steps[0]
        last_step = steps[1]

        self.logger.info(
            'Tour %s current step: %d, last step: %d',
            tour_selector, current_step, last_step)

        return current_step, last_step

    def open_announcements(self):
        """Opens Tours Guide Announcements menu."""

        # Tour Guide option button
        self.click_element(self.announcements_button)
        self.is_element_present(
            ToursGuideSelectors.LEFT_ARROW_BUTTON.value,
            raise_error=True
        )
        self.logger.info('Opened Tours Guide Announcements')

    def get_announcements_count(self):
        """Returns Announcements badge notifications count."""

        count = self.get_inner_text(
            ToursGuideSelectors.ANNOUNCEMENT_COUNT.value
        )
        self.logger.info('Announcements count: %s', count)

        return count

    def get_progress_bar_percent(self):
        """Returns Tour progress bar percent int value."""

        text = self.get_element_inner_text(self.progress_bar_section)
        percent_value = int(text.replace('%', ''))
        self.logger.info(
            'Tours progress bar percent: %s', percent_value
        )
        return percent_value

    def return_from_tour_announcements_details(self):
        """
        Clicks ANNOUNCEMENTS header to return from ANNOUNCEMENTS details
        to Tours Guide.
        """
        # the only option to successfully click the element
        sleep(5)
        self.click_element(self.announcements_button)
        self.is_element_present(
            ToursGuideSelectors.EXPLORE_DATAROBOT_GUIDE_HEADER.value,
            raise_error=True
        )
        self.logger.info('Returned from ANNOUNCEMENTS details')
