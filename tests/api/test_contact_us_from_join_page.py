from pytest import (
    fixture,
    mark
)

from utils.helper_funcs import (
    user_identity,
    get_query_param_value,
    update_rfc3339_date
)
from utils.http_utils.response_handler import ResponseHandler
from utils.constants import (
    CONTACT_US,
    NOT_STRING_ERROR,
    TRIAL_FLAGS
)
from utils.data_enums import ContactUsKeys
from utils.data_enums import UserType


TOPIC = 'Trial Support'
TEXT = 'TEST TEXT: 你好 Straße شارع тест'
REVISION = 'some_revision'


@fixture(scope='module')
def user_setup_and_teardown(app_client):
    username, first_name, last_name = user_identity()

    payload = {'userType': UserType.TRIAL_USER.value,
               'username': username,
               'firstName': first_name,
               'lastName': last_name,
               'expirationDate': update_rfc3339_date(
                   days=14, ahead=True),
               'requireClickthroughAgreement': False,
               'drAccountOptions': {'link': False},
               'permissionsDiff': TRIAL_FLAGS}

    resp = app_client.v2_create_user_request(payload)

    user_name = resp.json()['username']
    user_id = resp.json()['userId']
    code = get_query_param_value(resp.json()['notifyStatus']['inviteLink'], 'code')

    yield app_client, user_name, code, user_id

    app_client.v2_delete_payg_user(user_id)


@mark.contact_us
@mark.skip_if_env('staging')
def test_contact_us_from_join_page(user_setup_and_teardown):
    app_client, user_name, code, _ = user_setup_and_teardown

    resp = app_client.contact_us(username=user_name,
                                 invite_code=code,
                                 topic=TOPIC,
                                 text=TEXT,
                                 revision=REVISION,
                                 is_signed_up=False)

    assert _get_contact_us_status(resp) == 'ok'


@mark.contact_us
def test_contact_us_from_join_page_without_username_and_code(user_setup_and_teardown,
                                                             status_code,
                                                             resp_json):
    app_client, _, _, _ = user_setup_and_teardown

    resp = app_client.contact_us(topic=TOPIC,
                                 text=TEXT,
                                 revision=REVISION,
                                 check_status_code=False)

    assert status_code(resp) == 400
    assert resp_json(resp) == {'status': 'error',
                               'fields': {
                                   'username': 'is required',
                                   'code': 'is required'}}


@mark.contact_us
def test_contact_us_from_join_page_bad_code(user_setup_and_teardown,
                                            status_code,
                                            resp_json):
    app_client, user_name, _, _ = user_setup_and_teardown

    resp = app_client.contact_us(username=user_name,
                                 invite_code='non-existing invite code',
                                 topic=TOPIC,
                                 text=TEXT,
                                 revision=REVISION,
                                 is_signed_up=False,
                                 check_status_code=False)

    assert status_code(resp) == 422
    assert resp_json(resp) == {'message': 'Invalid username or code'}


@mark.contact_us
def test_contact_us_from_join_page_bad_username(user_setup_and_teardown,
                                                status_code,
                                                resp_json):
    app_client, _, code, _ = user_setup_and_teardown

    resp = app_client.contact_us(username='non-existing username',
                                 invite_code=code,
                                 topic=TOPIC,
                                 text=TEXT,
                                 revision=REVISION,
                                 is_signed_up=False,
                                 check_status_code=False)

    assert status_code(resp) == 422
    assert resp_json(resp) == {'message': 'Invalid username or code'}


@mark.contact_us
def test_contact_us_from_join_page_empty_username_and_code(user_setup_and_teardown,
                                                           status_code,
                                                           resp_json):
    app_client, _, _, _ = user_setup_and_teardown

    resp = app_client.contact_us(username='',
                                 invite_code='',
                                 topic=TOPIC,
                                 text=TEXT,
                                 revision=REVISION,
                                 is_signed_up=False,
                                 check_status_code=False)

    assert status_code(resp) == 400
    assert resp_json(resp) == {'status': 'error',
                               'fields': {
                                   'username': 'blank value is not allowed',
                                   'code': 'blank value is not allowed'}}


@mark.contact_us
def test_contact_us_from_join_page_username_and_code_not_str(user_setup_and_teardown,
                                                             status_code,
                                                             resp_json):
    app_client, _, _, _ = user_setup_and_teardown

    resp = app_client.contact_us(username=3,
                                 invite_code=3,
                                 topic=TOPIC,
                                 text=TEXT,
                                 revision=REVISION,
                                 is_signed_up=False,
                                 check_status_code=False)

    assert status_code(resp) == 400
    assert resp_json(resp) == {'status': 'error',
                               'fields': {
                                   'username': NOT_STRING_ERROR,
                                   'code': NOT_STRING_ERROR}}


@mark.contact_us
def test_contact_us_from_join_page_no_username(user_setup_and_teardown,
                                               status_code,
                                               resp_json):
    app_client, _, code, _ = user_setup_and_teardown

    payload = {'code': code,
               'topic': TOPIC,
               'text': TEXT,
               'revision': REVISION}

    resp = app_client.internal_api_post_request(
        CONTACT_US, payload, check_status_code=False)

    assert status_code(resp) == 400
    assert resp_json(resp) == {'fields': {'username': 'is required'},
                               'status': 'error'}


@mark.contact_us
def test_contact_us_from_join_page_no_code(user_setup_and_teardown,
                                           status_code,
                                           resp_json):
    app_client, user_name, _, _ = user_setup_and_teardown

    payload = {'username': user_name,
               'topic': TOPIC,
               'text': TEXT,
               'revision': REVISION}

    resp = app_client.internal_api_post_request(
        CONTACT_US, payload, check_status_code=False)

    assert status_code(resp) == 400
    assert resp_json(resp) == {'fields': {'code': 'is required'},
                               'status': 'error'}


@mark.contact_us
@mark.skip_if_env('staging')
def test_contact_us_from_join_page_no_topic(user_setup_and_teardown):
    app_client, user_name, code, _ = user_setup_and_teardown

    payload = {'username': user_name,
               'code': code,
               'text': TEXT,
               'revision': REVISION}

    resp = app_client.internal_api_post_request(CONTACT_US, payload)

    assert _get_contact_us_status(resp) == 'ok'


@mark.contact_us
def test_contact_us_from_join_page_no_text(user_setup_and_teardown,
                                           status_code,
                                           resp_json):
    app_client, user_name, code, _ = user_setup_and_teardown

    payload = {'username': user_name,
               'code': code,
               'topic': TOPIC,
               'revision': REVISION}

    resp = app_client.internal_api_post_request(
        CONTACT_US, payload, check_status_code=False)

    assert status_code(resp) == 400
    assert resp_json(resp) == {'fields': {'text': 'is required'},
                               'status': 'error'}


@mark.contact_us
@mark.skip_if_env('staging')
def test_contact_us_from_join_page_no_revision(user_setup_and_teardown):
    app_client, user_name, code, _ = user_setup_and_teardown

    payload = {'username': user_name,
               'code': code,
               'topic': TOPIC,
               'text': TEXT}

    resp = app_client.internal_api_post_request(CONTACT_US, payload)

    assert _get_contact_us_status(resp) == 'ok'


@mark.contact_us
@mark.skip_if_env('staging')
def test_contact_us_from_join_page_ui_non_supported_topic(user_setup_and_teardown):
    app_client, user_name, code, _ = user_setup_and_teardown

    payload = {'username': user_name,
               'code': code,
               'topic': 'Non-supported topic at UI',
               'text': TEXT,
               'revision': REVISION}

    resp = app_client.internal_api_post_request(CONTACT_US, payload)

    assert _get_contact_us_status(resp) == 'ok'


def _get_contact_us_status(resp):
    return ResponseHandler(resp).get_json_key_value(
        ContactUsKeys.STATUS.value)
