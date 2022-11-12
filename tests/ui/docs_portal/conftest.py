import logging

from pytest import fixture

from pages.docs_portal_pages import *
from utils.selectors_enums import DocsMainPageSelectors


LOGGER = logging.getLogger(__name__)


@fixture
def docs_base_page(page, env_params):
    return DocsBasePage(page, env_params)


@fixture
def docs_main_page(page, env_params):
    return DocsMainPage(page, env_params)


@fixture
def docs_platform_page(page, env_params):
    return DocsPlatformPage(page, env_params)


@fixture
def docs_platform_data_page(page, env_params):
    return DocsPlatformDataPage(page, env_params)


@fixture
def docs_search_component(page, env_params):
    return DocsSearchComponent(page, env_params)


@fixture(autouse=True)
def go_to_docs_portal(docs_base_page):
    """Goes to Docs Portal landing page. Auto-used for all tests"""

    docs_base_page.navigate(
        wait_for_element=True,
        selector=DocsMainPageSelectors.WELCOME_TO_DR_DOCUMENTATION_TITLE.value)
