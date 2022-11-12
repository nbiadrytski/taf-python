from pages.base_page import BasePage
from utils.selectors_enums import PendoTourSelectors
from utils.errors import ElementIsPresentException


class PendoTourPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def no_thanks_button(self):
        return self.wait_for_element(
            PendoTourSelectors.NO_THANKS_BUTTON.value)

    @property
    def remind_me_tomorrow_button(self):
        return self.wait_for_element(
            PendoTourSelectors.REMIND_ME_TOMORROW_BUTTON.value)

    @property
    def close_tour_x_button(self):
        return self.wait_for_element(
            PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value)

    @property
    def start_tour_button(self):
        return self.wait_for_element(
            PendoTourSelectors.START_TOUR_BUTTON.value)

    @property
    def show_me_around_button(self):
        return self.wait_for_element(
            PendoTourSelectors.SHOW_ME_AROUND_BUTTON.value)

    @property
    def back_button(self):
        return self.wait_for_element(
            PendoTourSelectors.BACK_BUTTON.value)

    @property
    def next_button(self):
        return self.wait_for_element(
            PendoTourSelectors.NEXT_BUTTON.value)

    @property
    def helpful_no_button(self):
        return self.wait_for_element(
            PendoTourSelectors.HELPFUL_NO_BUTTON.value)

    @property
    def helpful_yes_button(self):
        return self.wait_for_element(
            PendoTourSelectors.HELPFUL_YES_BUTTON.value)

    def start_tour(self, wait_for_back_button=True, tooltip_title=''):
        """Starts Pendo tour and waits either for Back button or next tooltip title to be present."""

        self.click_element(self.start_tour_button)
        log_message = 'Started Pendo tour'

        if wait_for_back_button:
            self.wait_for_element(PendoTourSelectors.BACK_BUTTON.value)
            self.logger.info(log_message)
        else:
            self.wait_for_element(
                f'strong:has-text("{tooltip_title}")'
            )
            self.logger.info(log_message)

    def start_home_tour(self):
        """
        Starts Pendo Home tour and
        waits for Next button at the following Data Prep tooltip.
        """
        self.click_element(self.show_me_around_button)
        self.is_element_present(
            PendoTourSelectors.NEXT_BUTTON.value,
            raise_error=True,
            help_text='Tooltip Next button is absent after starting Home tour'
        )
        self.logger.info('Started Home tour')

    def click_next_button(self):
        """Clicks Next button at Pendo tooltip"""

        self.click_element(self.next_button)
        self.logger.info('Clicked Pendo tooltip Next button')

    def click_was_tour_helpful_yes_button(self):
        self.click_element(self.helpful_yes_button)
        if self.is_element_present(
                PendoTourSelectors.HELPFUL_YES_BUTTON.value, timeout=5000,
                help_text='Was this tour helpful "Yes" button is still present'
                          ' after clicking it'):
            raise ElementIsPresentException(
                PendoTourSelectors.HELPFUL_YES_BUTTON.value)
