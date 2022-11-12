from enum import Enum

from pages.docs_portal_pages import DocsBasePage
from utils.selectors_enums import DocsCommonSelectors


class DocsPlatformDataPage(DocsBasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)


class PlatformDataPageSelectors(Enum):
    DATA_PAGE_TITLE = 'div.md-content #data'
    DATA_CONNECTIONS_PAGE_TITLE = 'div.md-content #data-connections'
    # NAVIGATION LINKS
    DATA_MANAGEMENT_NAV_LINK = DocsCommonSelectors.NAV_LINK.value.format(
        'data-mgmt/index.html')
    IMPORT_DATA_NAV_LINK = DocsCommonSelectors.NAV_LINK.value.format(
        'data-ingest/index.html')
    DATA_CONNECTIONS_LIST_NAV_LINK = DocsCommonSelectors.\
        NAV_LINKS_LIST_ITEM.value.format('data-conn.html')
    # BREADCRUMBS
    DATA_BC = DocsCommonSelectors.BREADCRUMB_TITLE.value.format('Data')
    DATA_MANAGEMENT_BC = DocsCommonSelectors.BREADCRUMB_TITLE.value.format(
        'Data Management')
    IMPORT_DATA_BC = DocsCommonSelectors.BREADCRUMB_TITLE.value.format(
        'Import data')
    DATA_CONNECTIONS_LAST_BC = DocsCommonSelectors.\
        LAST_BREADCRUMB_TITLE.value.format('Data connections')
