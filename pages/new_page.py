from pages.base_page import BasePage
from utils.selectors_enums import (
    NewPageSelectors,
    DataPageSelectors
)
from utils.helper_funcs import get_id_from_url


IMPORT_DATASET = ':text-is("Import dataset")'
DATASET_REQUIREMENTS_MODAL = 'Dataset Requirements modal'


class NewPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def ai_catalog_button(self):
        return self.wait_for_element(
            NewPageSelectors.AI_CATALOG_BUTTON.value)

    @property
    def hospital_readmission_import_button(self):
        return self.wait_for_element(
            f'{NewPageSelectors.HOSPITAL_READMISSION_DEMO_DATASET.value}'
            f' {IMPORT_DATASET}')

    @property
    def predict_late_shipment_import_button(self):
        return self.wait_for_element(
            f'{NewPageSelectors.PREDICT_LATE_SHIPMENT_DEMO_DATASET.value}'
            f' {IMPORT_DATASET}')

    @property
    def welcome_splash_modal_close_button(self):
        return self.wait_for_element(
            NewPageSelectors.WELCOME_SPLASH_MODAL_CLOSE_BUTTON.value)

    @property
    def view_dataset_requirements_button(self):
        return self.wait_for_element(
            NewPageSelectors.DATASETS_REQUIREMENTS_BUTTON.value)

    @property
    def dataset_requirements_modal_learn_more_button(self):
        return self.wait_for_element(
            NewPageSelectors.DATASETS_REQUIREMENTS_MODAL_LEARN_MORE_BUTTON.value)

    @property
    def dataset_requirements_modal_got_it_button(self):
        return self.wait_for_element(
            NewPageSelectors.DATASETS_REQUIREMENTS_MODAL_GOT_IT_BUTTON.value)

    @property
    def dataset_requirements_modal_close_button(self):
        return self.wait_for_element(
            NewPageSelectors.DATASETS_REQUIREMENTS_MODAL_CLOSE_BUTTON.value)

    def view_dataset_requirements(self):
        """Opens View Dataset Requirements modal."""

        self.click_element(self.view_dataset_requirements_button)
        self.is_element_present(
            NewPageSelectors.DATASETS_REQUIREMENTS_MODAL_TITLE.value, raise_error=True,
            help_text='Dataset Requirements modal was not opened'
        )
        self.logger.info('Opened Dataset Requirements modal')

    def import_demo_dataset(self, import_demo_dataset_button_element):
        """
        Imports demo dataset.
        Waits until: 'Recommended target is: {RECOMMENDED_TARGET_BUTTON}' is present.
        Returns project_id retrieved from page url.
        """
        self.click_element(import_demo_dataset_button_element)
        self.wait_for_element(
            DataPageSelectors.RECOMMENDED_TARGET_BUTTON.value,
            timeout=500000
        )
        project_id = get_id_from_url(self.page_url, 1)
        self.logger.info(
            'Imported demo dataset. Recommended target: %s. '
            'Project Id: %s',
            self.get_inner_text(
                DataPageSelectors.RECOMMENDED_TARGET_BUTTON.value),
            project_id
        )
        return project_id

    def close_welcome_splash_modal(self):
        """
        Waits for 'Welcome to the DataRobot AI Platform {first_name}' header at Welcome splash modal at /new page.
        Closes the modal by clicking Close X button in top right corner.
        """
        self.wait_for_element(
            NewPageSelectors.WELCOME_SPLASH_MODAL_FIRST_SLIDE_HEADER.value
        )
        self.click_element(
            self.welcome_splash_modal_close_button
        )
        self.logger.info('Closed Welcome splash modal at /new page')

    def click_dataset_requirements_modal_learn_more(self, docs_file_types_page):
        """
        Clicks 'Learn more' button from Dataset Requirements modal which initiates opening of
         /docs/load/file-types.html page in a new tab.
        """
        docs_page = 'docs/load/file-types.html page'
        learn_more_click = f'after clicking Learn more button from {DATASET_REQUIREMENTS_MODAL}'

        file_types_page = self.open_new_tab(
            self.dataset_requirements_modal_learn_more_button, docs_file_types_page
        )
        # Assert Dataset requirements title at /docs/load/file-types.html page
        file_types_page.is_element_present(
            selector='#dataset-requirements', timeout=20000, raise_error=True,
            help_text=f'{docs_page} did not open {learn_more_click}'
        )
        self.logger.info('Opened %s %s', docs_page, learn_more_click)

    def close_dataset_requirements_modal(self):
        """Closes Dataset Requirements modal by clicking Close X button."""

        self.click_element(self.dataset_requirements_modal_close_button)
        self.is_element_present(
            NewPageSelectors.AI_CATALOG_BUTTON.value, raise_error=True,
            help_text=f'Did not close {DATASET_REQUIREMENTS_MODAL}'
        )
        self.logger.info('Closed %s', DATASET_REQUIREMENTS_MODAL)

    def click_dataset_requirements_modal_got_it(self):
        """Closes Dataset Requirements modal by clicking 'Got it' button."""

        self.click_element(self.dataset_requirements_modal_got_it_button)
        self.is_element_present(
            NewPageSelectors.AI_CATALOG_BUTTON.value, raise_error=True,
            help_text=f'Did not close {DATASET_REQUIREMENTS_MODAL}'
        )
        self.logger.info('Closed %s', DATASET_REQUIREMENTS_MODAL)
