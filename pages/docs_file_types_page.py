from pages.base_page import BasePage


class DocsFileTypesPage(BasePage):
    """
    https://app2/staging.datarobot.com/docs/load/file-types.html page.
    Used in test_datasets_requirements test.
    """
    def __init__(self, page, env_params):
        super().__init__(page, env_params)
