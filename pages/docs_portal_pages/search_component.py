from time import sleep

from pages.docs_portal_pages import DocsBasePage
from utils.selectors_enums import DocsSearchSelectors
from utils.ui_constants import DEFAULT_TIMEOUT


class DocsSearchComponent(DocsBasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def search_field(self):
        return self.wait_for_element(
            DocsSearchSelectors.SEARCH_FIELD.value)

    def click_search_field(self):
        """
        Clicks Search field.
        Asserts 'data-focus-visible-added' attribute is present
        as an indicator of focused search field.
        """
        retry = 0
        max_retry = 20
        while True:
            retry += 1
            if retry >= 20:
                self.make_screenshot('search_field_not_focused')
                raise Exception(
                    f'Search field is not focused '
                    f'after clicking it {max_retry} times.')

            self.click_element(self.search_field)

            attribute_name = 'data-focus-visible-added'
            data_focus_visible_added_attribute = self.get_element_attribute_value(
                self.search_field, attribute_name
            )
            if data_focus_visible_added_attribute == '':
                break

            sleep(1)

            self.logger.info('Search is focused. Ready to type')

    def search(self, text):
        """
        Clicks Search field and types text into the field.
        Asserts search results area has '...results found' text now.
        """
        self.click_search_field()
        self.type_text(self.search_field, text, delay=200)
        self.is_element_present(
            DocsSearchSelectors.N_RESULTS_FOUND_TEXT.value,
            timeout=DEFAULT_TIMEOUT, raise_error=True,
            help_text='"...results found" text is missing '
                      'after typing text into Search field'
        )
        self.logger.info('Entered "%s" into Search field', text)
