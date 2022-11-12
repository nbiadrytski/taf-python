from pages.base_page import (
    BasePage,
    NAVIGATE_LOG_MESSAGE
)
from utils.data_enums import Envs
from utils.ui_constants import DEFAULT_TIMEOUT


class DocsBasePage(BasePage):

    def __init__(self, page, env_params):
        super().__init__(page, env_params)

        if env_params[0] == Envs.STAGING.value:
            self.docs_host = Envs.DOCS_STAGING.value
        else:
            self.docs_host = Envs.DOCS_PROD.value

    def navigate(self, path='', query_params='', wait_for_element=False,
                 selector='', timeout=DEFAULT_TIMEOUT):
        """
        Goes to page by provided path.
        Waits for page to load within timeout.
        Optionally accepts query params string.
        Optionally waits for element at the target page.

        Parameters
        ----------
        path : str
            Page path, e.g. /platform
        query_params : str
            Query params string
        wait_for_element : bool
            If to wait for element at target page or not
        selector : str
            Element selector
        timeout : int
            Wait for target page to load or
            element at target page is visible
        """
        if query_params is None:
            url = f'{self.docs_host}{path}?{query_params}'
        else:
            url = f'{self.docs_host}{path}'

        self.page.goto(url, timeout=timeout)

        if wait_for_element:
            self.wait_for_element(selector, timeout)
            self.logger.info(NAVIGATE_LOG_MESSAGE, url)
        else:
            self.logger.info(NAVIGATE_LOG_MESSAGE, url)

    def click_docs_nav_link(self, nav_item_selector):
        """
        Clicks Docs Portal navigation link at the left of doc page.

        Parameters
        ----------
        nav_item_selector : str
            Navigation list item selector
        """
        # extracts 'data-mgmt/index.html' from selector string, e.g.
        # label.md-nav__link >> css=[href="data-mgmt/index.html"]
        href = nav_item_selector[
               nav_item_selector.find('[') + 7:nav_item_selector.find('"]')]

        self.click_selector(nav_item_selector)

        if href not in self.page_url:
            raise ValueError(f'"{href}" is not a part of {self.page_url} url')
        self.logger.info(
            'User is at %s after clicking Docs Portal nav link %s',
            self.page_url, href)
