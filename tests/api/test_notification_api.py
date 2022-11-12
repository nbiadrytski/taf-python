from pytest import mark

from utils.constants import (
    NOTIFICATION_EVENT_TYPES,
    DEFAULT_USER_NOTIFICATIONS,
    API_V2_PATH,
    ASSERT_ERRORS,
    STATUS_ERROR_TEXT
)


RESP_ERROR_TEXT = 'Expected resp: {}, got: {}'

VALID_LIMIT_DATA = [(1, DEFAULT_USER_NOTIFICATIONS),
                    (1000, DEFAULT_USER_NOTIFICATIONS),
                    ('500', DEFAULT_USER_NOTIFICATIONS)]
LIMIT_TYPE_ERROR = {'message': {'limit': 'value can\'t be converted to int'}}
INVALID_LIMIT_DATA = [(0, 400, {'message': {'limit': 'value should be greater than 0'}}),
                      (1001, 400, {'message': {'limit': 'value is greater than 1000'}}),
                      (True, 400, LIMIT_TYPE_ERROR),
                      ('no', 400, LIMIT_TYPE_ERROR)]


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
def test_user_notifications_supported_event_types(
        app_client, user_setup_and_teardown, resp_json):
    event_types = resp_json(app_client.v2_get_notification_supported_event_types())

    assert event_types == NOTIFICATION_EVENT_TYPES, \
        f'Expected event types: {NOTIFICATION_EVENT_TYPES}, got: {event_types}'


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
@mark.parametrize('limit, expected_resp',
                  VALID_LIMIT_DATA,
                  ids=['limit=1', 'limit=1000', 'limit=\'500\''])
def test_user_notifications_valid_limit(
        app_client, user_setup_and_teardown, resp_json, limit, expected_resp):
    actual_resp = resp_json(
        app_client.v2_get_user_notifications(query_params={'limit': limit}))

    assert actual_resp == expected_resp, \
        RESP_ERROR_TEXT.format(expected_resp, actual_resp)


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
@mark.parametrize('limit, expected_code, expected_resp',
                  INVALID_LIMIT_DATA,
                  ids=['limit=0', 'limit=1001', 'limit=True', 'limit=no'])
def test_user_notifications_invalid_limit(
        app_client, user_setup_and_teardown, resp_json, status_code,
        limit, expected_code, expected_resp):

    resp = app_client.v2_api_get_request(f'{API_V2_PATH}/userNotifications/',
                                         query_params={'limit': limit},
                                         check_status_code=False)
    errors = []

    actual_code = status_code(resp)
    if actual_code != expected_code:
        errors.append(STATUS_ERROR_TEXT.format(expected_code, actual_code))

    actual_resp = resp_json(resp)
    if actual_resp != expected_resp:
        errors.append(RESP_ERROR_TEXT.format(expected_resp, actual_resp))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
