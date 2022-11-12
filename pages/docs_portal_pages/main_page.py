from pages.docs_portal_pages import DocsBasePage
from utils.selectors_enums import (
    DocsMainPageSelectors,
    DocsPlatformPageSelectors
)


class DocsMainPage(DocsBasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def platform_card_title(self):
        return self.wait_for_element(
            DocsMainPageSelectors.PLATFORM_CARD_TITLE.value)

    def go_to_platform_card_details(self):
        """Goes to Platform card details from Docs Portal landing page."""

        self.click_element(self.platform_card_title)
        self.is_element_present(
            DocsPlatformPageSelectors.DR_PLATFORM_DOCUMENTATION_TITLE.value,
            raise_error=True
        )
        self.logger.info('User is at %s page', self.page_url)
