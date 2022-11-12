import os

from pytest import mark

from utils.constants import (
    THIS_FILE_PARENT_DIR,
    TEST_FILES_PATH,
    ASSERT_ERRORS
)


QUERY_STRING = 'configure time-aware feature engineering'
QUERY_STRING_2_PAGES = 'using Import data from rep'


@mark.docs
def test_search_all(docs_client, get_dicts_diff):

    resp = docs_client.search(QUERY_STRING)

    # ignore dynamic values for processingTimeMS and objectID (for 3 hits) keys
    ignored_keys = (
        PROCESSING_TIME_KEY, OBJECT_ID_HIT_1, OBJECT_ID_HIT_2, OBJECT_ID_HIT_3
    )
    difference = get_dicts_diff(resp, DOCS_SEARCH_ALL, ignored_keys)

    assert not difference, f'Responses do not match. Diff:\n {difference}'


@mark.docs
def test_search_filter_by_platform(docs_client, get_dicts_diff):

    resp = docs_client.search(QUERY_STRING, filters='itemType:platform')

    ignored_keys = (PROCESSING_TIME_KEY, OBJECT_ID_HIT_1)
    difference = get_dicts_diff(resp, DOCS_SEARCH_PLATFORM, ignored_keys)

    assert not difference, f'Responses do not match. Diff:\n {difference}'


@mark.docs
def test_search_filter_by_api(docs_client, get_dicts_diff):

    resp = docs_client.search(QUERY_STRING, filters='itemType:api')

    ignored_keys = (PROCESSING_TIME_KEY, OBJECT_ID_HIT_1)
    difference = get_dicts_diff(resp, DOCS_SEARCH_API, ignored_keys)

    assert not difference, f'Responses do not match. Diff:\n {difference}'


@mark.docs
def test_search_filter_by_tutorials(docs_client, get_dicts_diff):

    resp = docs_client.search(QUERY_STRING, filters='itemType:tutorials')

    ignored_keys = (PROCESSING_TIME_KEY, OBJECT_ID_HIT_1, OBJECT_ID_HIT_2)
    difference = get_dicts_diff(resp, DOCS_SEARCH_TUTORIALS, ignored_keys)

    assert not difference, f'Responses do not match. Diff:\n {difference}'


@mark.docs
def test_search_multiple_pages(docs_client, get_dicts_diff, resp_json):

    resp_page0 = docs_client.search(QUERY_STRING_2_PAGES, page=0, filters=None)
    resp_page1 = docs_client.search(QUERY_STRING_2_PAGES, page=1, filters=None)

    ignored_keys_page0 = (
        PROCESSING_TIME_KEY, OBJECT_ID_HIT_1, OBJECT_ID_HIT_2,
        OBJECT_ID_HIT_3, OBJECT_ID_HIT_4, OBJECT_ID_HIT_5, OBJECT_ID_HIT_6,
        OBJECT_ID_HIT_7, OBJECT_ID_HIT_8, OBJECT_ID_HIT_9, OBJECT_ID_HIT_10
    )
    ignored_keys_page1 = (
        PROCESSING_TIME_KEY, OBJECT_ID_HIT_1, OBJECT_ID_HIT_2,
        OBJECT_ID_HIT_3, OBJECT_ID_HIT_4, OBJECT_ID_HIT_5
    )
    diff_page0 = get_dicts_diff(
        resp_page0, DOCS_SEARCH_PAGE_0, ignored_keys_page0
    )
    diff_page1 = get_dicts_diff(
        resp_page1, DOCS_SEARCH_PAGE_1, ignored_keys_page1)

    errors = []
    if diff_page0:
        errors.append(
            f'Pge 0 responses do not match. Diff:\n {diff_page0}'
            f'\nActual resp: {resp_json(resp_page0)}')
    if diff_page1:
        errors.append(
            f'Pge 1 responses do not match. Diff:\n {diff_page1}'
            f'\nActual resp: {resp_json(resp_page1)}')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


PROCESSING_TIME_KEY = ['results', 0, 'processingTimeMS']
OBJECT_ID_HIT_1 = ['results', 0, 'hits', 0, 'objectID']
OBJECT_ID_HIT_2 = ['results', 0, 'hits', 1, 'objectID']
OBJECT_ID_HIT_3 = ['results', 0, 'hits', 2, 'objectID']
OBJECT_ID_HIT_4 = ['results', 0, 'hits', 3, 'objectID']
OBJECT_ID_HIT_5 = ['results', 0, 'hits', 4, 'objectID']
OBJECT_ID_HIT_6 = ['results', 0, 'hits', 5, 'objectID']
OBJECT_ID_HIT_7 = ['results', 0, 'hits', 6, 'objectID']
OBJECT_ID_HIT_8 = ['results', 0, 'hits', 7, 'objectID']
OBJECT_ID_HIT_9 = ['results', 0, 'hits', 8, 'objectID']
OBJECT_ID_HIT_10 = ['results', 0, 'hits', 9, 'objectID']


DOCS_SEARCH_ALL = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_all.json')
DOCS_SEARCH_PLATFORM = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_platform.json')
DOCS_SEARCH_API = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_api.json')
DOCS_SEARCH_TUTORIALS = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_tutorials.json')
DOCS_SEARCH_PAGE_0 = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_page0.json')
DOCS_SEARCH_PAGE_1 = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_page1.json')
