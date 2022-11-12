from time import sleep

from pages.base_page import BasePage
from utils.selectors_enums import ModelingRightSidebarSelectors


class ModelingRightSidebar(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def pause_modeling_tasks_button(self):
        return self.wait_for_element(
            ModelingRightSidebarSelectors.PAUSE_MODELING_TASKS_BUTTON.value)

    @property
    def start_modeling_tasks_button(self):
        return self.wait_for_element(
            ModelingRightSidebarSelectors.START_MODELING_TASKS_BUTTON.value)

    @property
    def workers_count(self):
        return self.wait_for_element(
            ModelingRightSidebarSelectors.WORKERS_COUNT.value)

    @property
    def decrease_workers_button(self):
        return self.wait_for_element(
            ModelingRightSidebarSelectors.DECREASE_WORKERS_BUTTON.value)

    def pause_modeling_tasks(self):
        """Clicks 'Pause all tasks' button to pause modeling."""

        self.click_element(self.pause_modeling_tasks_button)
        self.is_element_present(
            ModelingRightSidebarSelectors.START_MODELING_TASKS_BUTTON.value,
            raise_error=True
        )
        self.logger.info('Paused modeling tasks.')

    def get_workers_count(self):
        """Get workers count (int) from modeling right sidebar."""

        count = self.get_element_inner_text(self.workers_count)
        self.logger.info('Workers count: %s', count)

        return int(count)

    def decrease_workers(self):
        """
        Decreases workers count by clicking 'Decrease workers' arrow button.
        Returns True if workers can be decreased, otherwise returns False.
        """
        workers_before_decreasing = self.get_workers_count()
        expected_workers_after_decreasing = workers_before_decreasing - 1

        if workers_before_decreasing <= 0:
            self.logger.warning(
                'Workers count: %d. Cannot decrease.',
                workers_before_decreasing
            )
            return False

        self.click_element(self.decrease_workers_button)

        workers_after_decreasing = self.get_workers_count()
        if workers_after_decreasing != expected_workers_after_decreasing:
            # give some time until workers count is changed
            sleep(4)
            workers_after_decreasing = self.get_workers_count()

        if workers_after_decreasing != expected_workers_after_decreasing:
            raise ValueError(
                f'Expected {expected_workers_after_decreasing} workers '
                f'after decreasing, got: {workers_after_decreasing}.'
            )
        self.logger.info(
            'Workers decreased from %d to %d.',
            workers_before_decreasing, workers_after_decreasing
        )
        return True
