from pytest import mark

from utils.helper_funcs import (
    generate_unique_email,
    generate_uuid,
    replace_chars_if_needed
)
from utils.constants import (
    DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
    PORTAL_ID_REQUIRED_ERROR,
    BOTH_PORTAL_ID_AND_EMAIL_ERROR,
    ASSERT_ERRORS,
    PORTAL_ID_QUERY_PARAM,
    EMAIL_NOT_VALID_ACCOUNT_ERROR,
    NOT_VALID_ACCOUNT_ERROR,
    PORTAL_ID_INVALID_FORMAT,
    EMAIL_QUERY_PARAM,
    INVALID_EMAIL_ERROR,
    STAGING_SELF_SERVICE_TEST_USER,
    ACCOUNT_NOT_YOURS_ERROR
)


@mark.dr_account_portal
def test_balance_summary_no_portal_id_or_email(dr_account_client, assert_json_resp,
                                               assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
                                                          check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_balance_summary_both_portal_id_and_email(portal_user_setup_teardown,
                                                  dr_account_client, auth0_token,
                                                  get_user_identity, assert_json_resp,
                                                  assert_status_code):

    resp = dr_account_client.dr_account_get_request(
        DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
        query_params=f'portalId={dr_account_client.portal_id}&'
                     f'email={replace_chars_if_needed(get_user_identity[0])}',
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=BOTH_PORTAL_ID_AND_EMAIL_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_cannot_get_not_yours_balance_summary_by_email(portal_user_setup_teardown, dr_account_client,
                                                       auth0_token, assert_json_resp,
                                                       assert_status_code):

    resp = dr_account_client.get_balance_summary(email=STAGING_SELF_SERVICE_TEST_USER,
                                                 check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_balance_summary_non_existing_portal_id(dr_account_client, assert_json_resp,
                                                assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
        query_params=PORTAL_ID_QUERY_PARAM.format(generate_uuid()),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_balance_summary_portal_id_str(dr_account_client, assert_json_resp,
                                       assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
        query_params=PORTAL_ID_QUERY_PARAM.format('test'),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': PORTAL_ID_INVALID_FORMAT},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_balance_summary_non_existing_email(dr_account_client, assert_json_resp,
                                            assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
        query_params=EMAIL_QUERY_PARAM.format(generate_unique_email()),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=EMAIL_NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_balance_summary_invalid_email(dr_account_client, assert_json_resp,
                                       assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
        query_params=EMAIL_QUERY_PARAM.format('invalid_email@'),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {'email': INVALID_EMAIL_ERROR}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_balance_summary_invalid_query_param(portal_user_setup_teardown, dr_account_client,
                                             auth0_token, assert_json_resp, assert_status_code):

    resp = dr_account_client.dr_account_get_request(
        DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
        query_params=f'portalId={str(dr_account_client.portal_id)}&new_param=test',
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {'new_param': 'new_param is not allowed key'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
