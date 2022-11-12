from urllib.parse import quote

from pytest import mark

from utils.helper_funcs import (
    generate_unique_email,
    generate_uuid
)
from utils.constants import (
    METERING_NO_CREDIT_USAGE_DETAILS_RESP,
    ERROR_JSON_RESP,
    METERING_START_TS_TZ,
    METERING_END_TS_TZ,
    METERING_START_TS_NO_TZ,
    METERING_END_TS_NO_TZ,
    ASSERT_ERRORS,
    DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
    STAGING_SELF_SERVICE_TEST_USER,
    ACCOUNT_NOT_YOURS_ERROR,
    NOT_VALID_ACCOUNT_ERROR,
    PORTAL_ID_ERROR
)
from utils.helper_funcs import (
    sort_list_of_dicts,
    sort_credits_system_data_dicts
)
from utils.data_enums import (
    CreditUsageDetailsKeys,
    MeteringType
)


DATA_LENGTH_ERROR_TEXT = 'data list length is not {}'


@mark.dr_account_portal
def test_get_credit_usage_details_start_ts_less_end_ts_more(dr_account_client,
                                                            register_single_user_data,
                                                            resp_json,
                                                            ml_category,
                                                            mm_category,
                                                            purchase_category,
                                                            prediction_category):
    register_single_user_data()

    resp = resp_json(
        dr_account_client.get_credit_usage_details('2020-07-07T08:00:00Z',
                                                   '2020-08-08T11:00:00Z',
                                                   dr_account_client.portal_id))
    actual_resp = sort_credits_system_data_dicts(resp)

    expected_resp = {
        'totalCount': 4,
        'data': sort_list_of_dicts([ml_category(),
                                    mm_category(),
                                    purchase_category(),
                                    prediction_category()])}

    assert actual_resp == expected_resp, \
        ERROR_JSON_RESP.format(
            'with earlier start and later end date', expected_resp, actual_resp)


@mark.dr_account_portal
def test_no_credit_usage_details_start_ts_more_end_ts_same(dr_account_client,
                                                           register_single_user_data,
                                                           give_initial_credits,
                                                           resp_json):
    register_single_user_data()

    resp = resp_json(
        dr_account_client.get_credit_usage_details('2020-08-07T08:00:01Z',
                                                   METERING_END_TS_TZ,
                                                   dr_account_client.portal_id))

    assert resp == METERING_NO_CREDIT_USAGE_DETAILS_RESP, \
        ERROR_JSON_RESP.format(
            'with start date 1 second more and same end date',
            METERING_NO_CREDIT_USAGE_DETAILS_RESP, resp)


@mark.dr_account_portal
def test_no_credit_usage_details_start_ts_same_end_ts_less(dr_account_client,
                                                           register_single_user_data,
                                                           give_initial_credits,
                                                           resp_json):
    register_single_user_data()

    resp = resp_json(
        dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                   '2020-08-08T07:59:59Z',
                                                   dr_account_client.portal_id))

    assert resp == METERING_NO_CREDIT_USAGE_DETAILS_RESP, \
        ERROR_JSON_RESP.format(
            'with start date 1 second more and same end date',
            METERING_NO_CREDIT_USAGE_DETAILS_RESP, resp)


@mark.dr_account_portal
def test_credit_usage_details_invalid_params(portal_user_setup_teardown,
                                             dr_account_client,
                                             auth0_token,
                                             assert_status_code,
                                             assert_json_resp):

    resp = dr_account_client.get_credit_usage_details(
        start_ts=METERING_START_TS_NO_TZ,
        end_ts=METERING_END_TS_NO_TZ,
        portal_id=dr_account_client.portal_id,
        metering_type='invalidType',
        offset=False,
        limit=True,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {
            'billingPeriodStartTs': 'value does not match format %Y-%m-%dT%H:%M:%S%z',
            'billingPeriodEndTs': 'value does not match format %Y-%m-%dT%H:%M:%S%z',
            'meteringType': 'value is not a valid metering type',
            'limit': 'value can\'t be converted to int',
            'offset': 'value can\'t be converted to int'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_required_params_email(portal_user_setup_teardown,
                                                    dr_account_client,
                                                    auth0_token,
                                                    resp_json,
                                                    get_user_identity):
    resp = resp_json(
        dr_account_client.get_credit_usage_details(start_ts=METERING_START_TS_TZ,
                                                   end_ts=METERING_END_TS_TZ,
                                                   email=quote(get_user_identity[0])))

    expected_resp = {'data': [], 'totalCount': 0}

    assert resp == expected_resp, \
        ERROR_JSON_RESP.format(
            'with email instead of portalId', expected_resp, resp)


@mark.dr_account_portal
def test_credit_usage_details_no_params(dr_account_client,
                                        assert_status_code,
                                        assert_json_resp):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={
            'errors':
                {'portalId': 'one of `portalId` and `email` is required',
                 'email': 'one of `portalId` and `email` is required',
                 'billingPeriodStartTs': 'is required',
                 'billingPeriodEndTs': 'is required'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_both_portalid_and_email(dr_account_client,
                                                      assert_status_code,
                                                      assert_json_resp,
                                                      admin_portal_id):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
        f'portalId={admin_portal_id}&'
        f'email={quote(STAGING_SELF_SERVICE_TEST_USER)}&'
        f'billingPeriodStartTs={METERING_START_TS_TZ}&'
        f'billingPeriodEndTs={METERING_END_TS_TZ}',
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors':
                           {'email': 'invalid when portalId is provided',
                            'portalId': 'invalid when email is provided'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_email_not_yours(portal_user_setup_teardown,
                                              dr_account_client,
                                              auth0_token,
                                              assert_status_code,
                                              assert_json_resp,
                                              resp_json):

    resp = dr_account_client.get_credit_usage_details(
        start_ts=METERING_START_TS_TZ,
        end_ts=METERING_END_TS_TZ,
        email=quote(STAGING_SELF_SERVICE_TEST_USER),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_portal_id_not_yours(portal_user_setup_teardown,
                                                  dr_account_client,
                                                  auth0_token,
                                                  admin_portal_id,
                                                  assert_status_code,
                                                  assert_json_resp):

    resp = dr_account_client.get_credit_usage_details(
        start_ts=METERING_START_TS_TZ,
        end_ts=METERING_END_TS_TZ,
        portal_id=admin_portal_id,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_non_existing_email(dr_account_client,
                                                 assert_status_code,
                                                 assert_json_resp,
                                                 resp_json):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
        f'email={quote(generate_unique_email())}&'
        f'billingPeriodStartTs={METERING_START_TS_TZ}&'
        f'billingPeriodEndTs={METERING_END_TS_TZ}',
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {'email': 'not a valid account'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_non_existing_portal_id(dr_account_client,
                                                     assert_status_code,
                                                     assert_json_resp,
                                                     resp_json):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
        f'portalId={generate_uuid()}&'
        f'billingPeriodStartTs={METERING_START_TS_TZ}&'
        f'billingPeriodEndTs={METERING_END_TS_TZ}',
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_mm_job_metering_type(dr_account_client,
                                                   resp_json,
                                                   register_single_user_data,
                                                   mm_category):
    register_single_user_data()

    resp = resp_json(
        dr_account_client.get_credit_usage_details(
            METERING_START_TS_TZ,
            METERING_END_TS_TZ,
            dr_account_client.portal_id,
            metering_type=MeteringType.MMJOB.value))

    expected_resp = {'totalCount': 1,
                     'data': [mm_category()]}

    assert resp == expected_resp, \
        ERROR_JSON_RESP.format(
            'filtered by mmJob metering type', expected_resp, resp)


@mark.dr_account_portal
def test_credit_usage_details_prediction_metering_type(dr_account_client,
                                                       resp_json,
                                                       register_single_user_data,
                                                       prediction_category):
    register_single_user_data()

    resp = resp_json(
        dr_account_client.get_credit_usage_details(
            METERING_START_TS_TZ,
            METERING_END_TS_TZ,
            dr_account_client.portal_id,
            metering_type=MeteringType.PREDICTIONS.value))

    expected_resp = {'totalCount': 1,
                     'data': [prediction_category()]}

    assert resp == expected_resp, \
        ERROR_JSON_RESP.format(
            'filtered by prediction metering type', expected_resp, resp)


@mark.dr_account_portal
def test_credit_usage_details_deployment_uptime_metering_type(dr_account_client,
                                                              resp_json,
                                                              register_single_user_data,
                                                              ml_category):
    register_single_user_data()

    resp = resp_json(
        dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                   METERING_END_TS_TZ,
                                                   dr_account_client.portal_id,
                                                   metering_type=MeteringType.DEPLOYMENT.value))
    expected_resp = {'totalCount': 1,
                     'data': [ml_category()]}

    assert resp == expected_resp, \
        ERROR_JSON_RESP.format(
            'filtered by deploymentUptime metering type', expected_resp, resp)


@mark.dr_account_portal
def test_credit_usage_details_offset(dr_account_client,
                                     register_single_user_data,
                                     assert_key_in_resp,
                                     get_value_from_json_response):
    register_single_user_data()

    resp = dr_account_client.get_credit_usage_details(
        METERING_START_TS_TZ,
        METERING_END_TS_TZ,
        dr_account_client.portal_id,
        offset=3)

    errors = []
    assert_key_in_resp(resp,
                       key=CreditUsageDetailsKeys.TOTAL_COUNT.value,
                       expected_value=4,
                       errors_list=errors)
    data_list = get_value_from_json_response(
        resp, CreditUsageDetailsKeys.DATA.value)

    if len(data_list) != 1:
        errors.append(DATA_LENGTH_ERROR_TEXT.format('1'))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_limit(dr_account_client,
                                    register_single_user_data,
                                    assert_key_in_resp,
                                    get_value_from_json_response):
    register_single_user_data()

    resp = dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                      METERING_END_TS_TZ,
                                                      dr_account_client.portal_id,
                                                      limit=1)
    errors = []
    assert_key_in_resp(resp,
                       key=CreditUsageDetailsKeys.TOTAL_COUNT.value,
                       expected_value=4,
                       errors_list=errors)
    data_list = get_value_from_json_response(
        resp, CreditUsageDetailsKeys.DATA.value)

    if len(data_list) != 1:
        errors.append(DATA_LENGTH_ERROR_TEXT.format('1'))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_credit_usage_details_limit_offset(dr_account_client,
                                           register_single_user_data,
                                           assert_key_in_resp,
                                           get_value_from_json_response):
    register_single_user_data()

    resp = dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                      METERING_END_TS_TZ,
                                                      dr_account_client.portal_id,
                                                      limit='3',
                                                      offset='1')
    errors = []
    assert_key_in_resp(resp,
                       key=CreditUsageDetailsKeys.TOTAL_COUNT.value,
                       expected_value=4,
                       errors_list=errors)
    data_list = get_value_from_json_response(
        resp, CreditUsageDetailsKeys.DATA.value)

    if len(data_list) != 3:
        errors.append(DATA_LENGTH_ERROR_TEXT.format('3'))

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_get_credit_usage_details_for_deleted_user(portal_user_setup,
                                                   dr_account_client,
                                                   auth0_token,
                                                   assert_status_code,
                                                   assert_json_resp):
    portal_id = dr_account_client.portal_id
    dr_account_client.delete_user(portal_id)

    resp = dr_account_client.get_credit_usage_details(METERING_START_TS_TZ,
                                                      METERING_END_TS_TZ,
                                                      portal_id=portal_id,
                                                      check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_ERROR,
        errors_list=errors)
