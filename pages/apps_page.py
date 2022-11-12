from pages.base_page import BasePage
from utils.selectors_enums import AppsPageSelectors


class AppsPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def open_app_button(self):
        return self.wait_for_element(
            AppsPageSelectors.OPEN_APP_BUTTON.value)

    def open_app(self, app_page_title, app_page_object):
        """
        Opens App in a new tab by clicking 'Open' button from /applications page.
        'app_page_object' param is an object of new app Page, e.g. WhatIfAppPage.
        'app_page_title' param is a new page <title> tag value.
        Raises ValueError if actual_title != app_page_title.
        Returns BasePage object which allows further actions with the app page.
        """
        app_page = self.open_new_tab(self.open_app_button,
                                     app_page_object)

        actual_title = app_page.page_title
        if actual_title != app_page_title:
            raise ValueError(
                f'Expected page title "{app_page_title}",'
                f' got "{actual_title}".'
            )
        self.logger.info(
            'Opened %s app.', app_page_title
        )
        return app_page
