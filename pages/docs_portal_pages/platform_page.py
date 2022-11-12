from pages.docs_portal_pages import DocsBasePage
from utils.selectors_enums import (
    DocsPlatformPageSelectors,
)
from pages.docs_portal_pages.platform_data_page import PlatformDataPageSelectors


class DocsPlatformPage(DocsBasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def data_card_title(self):
        return self.wait_for_element(
            DocsPlatformPageSelectors.DATA_CARD_TITLE.value)

    def go_to_data_card_details(self):
        """Goes to Data card details from Platform page."""

        self.click_element(self.data_card_title)
        self.is_element_present(
            PlatformDataPageSelectors.DATA_PAGE_TITLE.value,
            raise_error=True,
            help_text='Could not navigate to Data card from Platform page'
        )
        self.logger.info('User is at %s page', self.page_url)
