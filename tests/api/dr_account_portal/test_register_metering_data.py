from pytest import (
    mark,
    fixture
)

from utils.helper_funcs import (
    convert_json_to_dict,
    generate_unique_email,
    sort_credits_system_data_dicts,
    sort_list_of_dicts
)
from utils.constants import (
    ASSERT_ERRORS,
    INVALID_CREDITS_FIELDS_RESP,
    ERROR_JSON_RESP,
    METERING_START_TS_TZ,
    METERING_END_TS_TZ,
    METERING_START_TS_NO_TZ,
    METERING_END_TS_NO_TZ,
    ID_24_CHARS,
    CREDIT_DETAILS_NO_REQUIRED_FIELDS_RESP,
    DR_ACCOUNT_PORTAL_REG_METER_DATA_PATH,
    ADMIN_PERMISSIONS_ERROR
)
from utils.data_enums import CreditsSystemDataSource


RESP_DO_NOT_MATCH_ERROR_TEXT = 'Responses do not match after registering data {} time'


@mark.dr_account_portal
def test_register_valid_metering_data_one_user(dr_account_client,
                                               metering_data,
                                               resp_json,
                                               ml_category,
                                               mm_category,
                                               prediction_category,
                                               purchase_category):

    dr_account_client.admin_register_metering_data(metering_data(1.5))

    resp = resp_json(dr_account_client.get_credit_usage_details(
        METERING_START_TS_TZ,
        METERING_END_TS_TZ,
        dr_account_client.portal_id))
    actual_resp = sort_credits_system_data_dicts(resp)

    expected_resp = {
        'totalCount': 4,
        'data': sort_list_of_dicts([ml_category(),
                                    mm_category(),
                                    purchase_category(),
                                    prediction_category()])
    }
    assert actual_resp == expected_resp, \
        ERROR_JSON_RESP.format(
            'for a single user', expected_resp, actual_resp)


@mark.dr_account_portal
def test_register_metering_data_same_user_different_period_twice(dr_account_client,
                                                                 metering_data,
                                                                 assert_json_resp,
                                                                 ml_category,
                                                                 mm_category,
                                                                 purchase_category,
                                                                 prediction_category,
                                                                 resp_json):
    portal_id = dr_account_client.portal_id

    dr_account_client.admin_register_metering_data(
        metering_data(value=1.5,
                      start='2019-09-10T08:00:00+00:00',
                      end='2019-09-11T08:00:00+00:00'))
    resp_1 = resp_json(
        dr_account_client.get_credit_usage_details('2019-09-10T08:00:00Z',
                                                   '2019-09-11T08:00:00Z',
                                                   portal_id))
    actual_resp_1 = sort_credits_system_data_dicts(resp_1)
    expected_resp_1 = {
        'totalCount': 4,
        'data': sort_list_of_dicts([ml_category(),
                                    mm_category(),
                                    purchase_category(),
                                    prediction_category()])}

    dr_account_client.admin_register_metering_data(
        metering_data(value=1.8,
                      start='2019-09-13T08:00:00+00:00',
                      end='2019-09-14T08:00:00+00:00'))
    resp_2 = resp_json(
        dr_account_client.get_credit_usage_details('2019-09-13T08:00:00Z',
                                                   '2019-09-14T08:00:00Z',
                                                   portal_id))
    actual_resp_2 = sort_credits_system_data_dicts(resp_2)
    expected_resp_2 = {
        'totalCount': 4,
        'data': sort_list_of_dicts([ml_category(1.8),
                                    mm_category(3.7),
                                    purchase_category(3.799),
                                    prediction_category(3.79)])}
    errors = []
    if actual_resp_1 != expected_resp_1:
        errors.append(RESP_DO_NOT_MATCH_ERROR_TEXT.format('1st'))
    if actual_resp_2 != expected_resp_2:
        errors.append(RESP_DO_NOT_MATCH_ERROR_TEXT.format('2nd'))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_register_metering_data_for_same_user_same_period_twice(dr_account_client,
                                                                metering_data,
                                                                assert_json_resp,
                                                                ml_category,
                                                                mm_category,
                                                                purchase_category,
                                                                prediction_category,
                                                                resp_json):
    dr_account_client.admin_register_metering_data(
        metering_data(value=1.5,
                      start=METERING_START_TS_NO_TZ,
                      end=METERING_END_TS_NO_TZ))
    resp_1 = resp_json(
        dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                   METERING_END_TS_TZ,
                                                   dr_account_client.portal_id))
    actual_resp_1 = sort_credits_system_data_dicts(resp_1)

    dr_account_client.admin_register_metering_data(
        metering_data(value=1.8,
                      start=METERING_START_TS_NO_TZ,
                      end=METERING_END_TS_NO_TZ))
    resp_2 = resp_json(
        dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                   METERING_END_TS_TZ,
                                                   dr_account_client.portal_id))
    actual_resp_2 = sort_credits_system_data_dicts(resp_2)

    expected_resp = {
        'totalCount': 4,
        'data': sort_list_of_dicts([ml_category(),
                                    mm_category(),
                                    purchase_category(),
                                    prediction_category()])}
    errors = []
    if actual_resp_1 != expected_resp:
        errors.append(RESP_DO_NOT_MATCH_ERROR_TEXT.format('1st'))
    if actual_resp_2 != expected_resp:
        errors.append(RESP_DO_NOT_MATCH_ERROR_TEXT.format('2nd'))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_register_valid_metering_data_two_users(dr_account_client,
                                                metering_data,
                                                resp_json,
                                                ml_category,
                                                mm_category,
                                                purchase_category,
                                                prediction_category):

    dr_account_client.admin_register_metering_data(
        metering_data(value=33.598,
                      single_user=False))

    resp = resp_json(
        dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                   METERING_END_TS_TZ,
                                                   dr_account_client.portal_id))
    actual_resp = sort_credits_system_data_dicts(resp)

    expected_resp = {
        'totalCount': 8,
        'data': sort_list_of_dicts([ml_category(33.598),
                                    mm_category(35.498),
                                    purchase_category(35.597),
                                    prediction_category(35.588),
                                    ml_category(33.598),
                                    mm_category(35.498),
                                    purchase_category(35.597),
                                    prediction_category(35.588)])}

    assert actual_resp == expected_resp, \
        ERROR_JSON_RESP.format('for 2 users', expected_resp, actual_resp)


@mark.dr_account_portal
def test_register_metering_data_2nd_user_doesnt_exist(dr_account_client,
                                                      resp_json,
                                                      metering_payload_2nd_user_doesnt_exist):

    dr_account_client.admin_register_metering_data(metering_payload_2nd_user_doesnt_exist)

    resp = resp_json(dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                                METERING_END_TS_TZ,
                                                                dr_account_client.portal_id))
    expected_resp = {'data': [{'category': 'Random category 1',
                               'creditUsage': 0.5,
                               'deploymentId': None,
                               'deploymentLabel': None,
                               'projectId': None,
                               'projectName': None}],
                     'totalCount': 1}

    assert resp == expected_resp, \
        ERROR_JSON_RESP.format('with 2nd non-existing user', expected_resp, resp)


@mark.dr_account_portal
def test_register_invalid_metering_data(dr_account_client,
                                        invalid_metering_payload,
                                        assert_json_resp,
                                        assert_status_code):

    resp = dr_account_client.admin_register_metering_data(
        invalid_metering_payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=convert_json_to_dict(INVALID_CREDITS_FIELDS_RESP),
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_register_metering_data_no_required_fields(dr_account_client,
                                                   invalid_metering_payload,
                                                   assert_json_resp,
                                                   assert_status_code):

    resp = dr_account_client.admin_register_metering_data(
        {'activeUsers': [{'operations': [{'operationDetails': {}}]}]},
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=convert_json_to_dict(CREDIT_DETAILS_NO_REQUIRED_FIELDS_RESP),
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_non_admin_cannot_register_metering_data(portal_user_setup_teardown,
                                                 dr_account_client,
                                                 auth0_token,
                                                 metering_data_with_payg,
                                                 assert_status_code,
                                                 assert_json_resp):

    resp = dr_account_client.dr_account_post_request(
        DR_ACCOUNT_PORTAL_REG_METER_DATA_PATH,
        request_body=metering_data_with_payg,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ADMIN_PERMISSIONS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def metering_payload_2nd_user_doesnt_exist(new_user_auth0_token):
    username, user_id = new_user_auth0_token
    return {  # only required fields
        'billingPeriodStartTs': METERING_START_TS_NO_TZ,
        'billingPeriodEndTs': METERING_END_TS_NO_TZ,
        'activeUsers': [
            {'email': username,
             'uid': user_id,
             'operations': [{'operationDetails': {'category': 'Random category 1'},
                             'source': CreditsSystemDataSource.PURCHASE.value,
                             'value': 0.5}]},
            {'email': generate_unique_email(),
             'uid': ID_24_CHARS,
             'operations': [{'operationDetails': {'category': 'Random category 2'},
                             'source': CreditsSystemDataSource.METERING.value,
                             'value': 10}]}]}


@fixture
def invalid_metering_payload():
    return {'billingPeriodStartTs': '2019-08-07T08:00:00+00:00_',
            'billingPeriodEndTs': '2028-08-07T08:00:00',
            'billingPeriodMiddleTs': METERING_START_TS_NO_TZ,
            'activeUsers': [
                {'email': 'invalid_email$test.com',
                 'uid': ID_24_CHARS + '1',
                 'password': 'password',
                 'operations': [{'projectId': ID_24_CHARS + '1',
                                 'deploymentId': 1,
                                 'modelId': '123',
                                 'operationDetails': {
                                     'projectName': 123,
                                     'deploymentLabel': 2,
                                     'type': 0,
                                     'category': 1.2,
                                     'workerSize': 1.4,
                                     'executionTimeMilliseconds': 'test',
                                     'uptimeSeconds': 'test',
                                     'limits': None},
                                 'source': 'INVALID_SOURCE',
                                 'metricType': 'INVALID_METRIC_TYPE',
                                 'value': -10}]},
                {'email': None,
                 'uid': '1',
                 'operations': [{'projectId': None,
                                 'deploymentId': '1',
                                 'operationDetails': {
                                     'projectName': None,
                                     'deploymentLabel': None,
                                     'type': 0.99,
                                     'category': None,
                                     'workerSize': False,
                                     'executionTimeMilliseconds': 4.56,
                                     'uptimeSeconds': 33.33},
                                 'source': 1,
                                 'metricType': 0,
                                 'value': 'test',
                                 'amount': 123}]}]}
