from pytest import (
    mark,
    fixture
)

from utils.selectors_enums import (
    DocsCommonSelectors,
    DocsSearchSelectors
)
from pages.docs_portal_pages.platform_data_page import PlatformDataPageSelectors
from utils.constants import ASSERT_ERRORS
from utils.data_enums import HtmlAttribute


SEARCH_QUERY = 'You can connect Data Prep to multiple SMB shares'


@mark.docs_portal_ui
def test_docs_user_basic_flow(
        assert_element_is_present, docs_main_page, docs_platform_page,
        docs_platform_data_page, assert_toc_items, assert_toc_nested_items,
        assert_data_connections_breadcrumbs, assert_toc_nested_twice_items,
        docs_search_component, assert_results_found_count,
        assert_search_result_item_link
):
    errors = []

    # -------------------------------------------------------------------------
    # 1. Go to Platform card from portal landing page
    # -------------------------------------------------------------------------
    docs_main_page.go_to_platform_card_details()

    # -------------------------------------------------------------------------
    # 2. Go to Data card from Platform card
    # -------------------------------------------------------------------------
    docs_platform_page.go_to_data_card_details()

    # -------------------------------------------------------------------------
    # 3. Go to Data > Data Management > Import data > Data connections
    # -------------------------------------------------------------------------
    docs_platform_data_page.click_docs_nav_link(
        PlatformDataPageSelectors.DATA_MANAGEMENT_NAV_LINK.value)
    docs_platform_data_page.click_docs_nav_link(
        PlatformDataPageSelectors.IMPORT_DATA_NAV_LINK.value)
    docs_platform_data_page.click_docs_nav_link(
        PlatformDataPageSelectors.DATA_CONNECTIONS_LIST_NAV_LINK.value)

    # -------------------------------------------------------------------------
    # 4. Assert Data connections page title
    # -------------------------------------------------------------------------
    assert_element_is_present(
        docs_platform_data_page,
        PlatformDataPageSelectors.DATA_CONNECTIONS_PAGE_TITLE.value,
        errors, 'Data Connections page title is missing')

    # -------------------------------------------------------------------------
    # 5. Assert Data connections page breadcrumbs
    # -------------------------------------------------------------------------
    assert_data_connections_breadcrumbs(errors)

    # -------------------------------------------------------------------------
    # 6. Assert Data connections TOC
    # -------------------------------------------------------------------------
    assert_toc_items(errors, docs_platform_data_page, TOC_ITEMS)
    assert_toc_nested_items(errors, docs_platform_data_page, TOC_NESTED_ITEMS)
    assert_toc_nested_twice_items(
        errors, docs_platform_data_page, TOC_NESTED_TWICE_ITEMS)

    # -------------------------------------------------------------------------
    # 7. Search for 'You can connect Data Prep to multiple SMB shares'
    # -------------------------------------------------------------------------
    docs_search_component.click_search_field()
    docs_search_component.search(SEARCH_QUERY)

    # -------------------------------------------------------------------------
    # 8. Assert matching documents count is 1
    # -------------------------------------------------------------------------
    assert_results_found_count(errors, '1')

    # -------------------------------------------------------------------------
    # 9. Assert search result item link
    # -------------------------------------------------------------------------
    assert_search_result_item_link(
        errors,
        'data/data-prep-pax/dp-connect/dp-conn-network-share-smb.html')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def assert_data_connections_breadcrumbs(
        assert_element_is_present, docs_platform_data_page
):
    """
    Asserts Data > Data Management > Import data > Data connections breadcrumbs
     are present at Platform Data page
     """
    def data_connections_breadcrumbs(errors_list):

        assert_element_is_present(
            docs_platform_data_page, PlatformDataPageSelectors.DATA_BC.value,
            errors_list, 'Start breadcrumb Data is missing')
        assert_element_is_present(
            docs_platform_data_page,
            PlatformDataPageSelectors.DATA_MANAGEMENT_BC.value,
            errors_list, 'Breadcrumb Data Management is missing')
        assert_element_is_present(
            docs_platform_data_page,
            PlatformDataPageSelectors.IMPORT_DATA_BC.value,
            errors_list, 'Breadcrumb Import Data is missing')
        assert_element_is_present(
            docs_platform_data_page,
            PlatformDataPageSelectors.DATA_CONNECTIONS_LAST_BC.value,
            errors_list, 'Last breadcrumb Data Connections is missing')

    return data_connections_breadcrumbs


@fixture
def assert_toc_items(assert_element_is_present):
    """
    Accepts a list of toc items strings and
    asserts that each TOC item is present at current page.
    TOC item is a value passed to DocsCommonSelectors.TOC_ITEM selector.
    """
    def assert_toc_items(errors_list, page, toc_items):

        for item in toc_items:

            assert_element_is_present(
                page, DocsCommonSelectors.TOC_ITEM.value.format(item),
                errors_list, f'TOC item {item} is missing')

    return assert_toc_items


@fixture
def assert_toc_nested_items(assert_element_is_present):
    """
    Accepts a list of toc nested items strings and
    asserts that each TOC item is present at current page.
    Nested TOC item is a value passed to
    DocsCommonSelectors.TOC_NESTED_ITEM selector.
    """
    def assert_toc_items(errors_list, page, toc_nested_items):

        for item in toc_nested_items:

            assert_element_is_present(
                page, DocsCommonSelectors.TOC_NESTED_ITEM.value.format(item),
                errors_list, f'Nested TOC item {item} is missing')

    return assert_toc_items


@fixture
def assert_toc_nested_twice_items(assert_element_is_present):
    """
    Accepts a list of toc nested twice items strings and
    asserts that each TOC item is present at current page.
    Nested twice TOC item is a value passed to
    DocsCommonSelectors.TOC_NESTED_TWICE_ITEM selector.
    """
    def assert_toc_items(errors_list, page, toc_nested_twice_items):

        for item in toc_nested_twice_items:

            assert_element_is_present(
                page,
                DocsCommonSelectors.TOC_NESTED_TWICE_ITEM.value.format(item),
                errors_list, f'Nested twice TOC item {item} is missing')

    return assert_toc_items


@fixture
def assert_results_found_count(
        assert_element_is_present, docs_search_component
):
    """Asserts number of results found after searching"""

    def results_found_count(errors_list, results_count):
        assert_element_is_present(
            docs_search_component,
            DocsSearchSelectors.N_RESULTS_FOUND.value.format(results_count),
            errors_list, f'Results count is not {results_count}')

    return results_found_count


@fixture
def assert_search_result_item_link(
        docs_search_component, assert_attribute_value_contains
):
    """Asserts search result item href attribute"""

    def search_result_item_link(errors_list, href):

        assert_attribute_value_contains(
            docs_search_component, DocsSearchSelectors.SEARCH_ITEM_HREF.value,
            HtmlAttribute.HREF.value, href, errors_list,
            help_text=f'Href attr of search item does not contain {href}')

    return search_result_item_link


TOC_ITEMS = [
    'Supported databases', 'Deprecated databases',
    'Database connectivity workflow', 'Create a new connection',
    'Work with data sources', 'Share data connections',
    'Database connection terms'
]
TOC_NESTED_ITEMS = [
    'Data connection with parameters', 'Test the connection',
    'Modify a connection', 'Delete a connection', 'Add data sources'
]
TOC_NESTED_TWICE_ITEMS = [
    'Tables tab', 'SQL Query tab'
]
