from pytest import mark

from utils.constants import (
    ASSERT_ERRORS,
    PORTAL_ID_REQUIRED_ERROR,
    ERROR_STATUS_CODE_RESPONSE,
    PORTAL_ID_QUERY_PARAM,
    ERROR_JSON_RESP,
    DR_ACCOUNT_ROLES_PATH,
    IS_ADMIN,
    IS_NOT_ADMIN,
    NOT_VALID_ACCOUNT_ERROR
)
from utils.helper_funcs import generate_uuid


@mark.dr_account_portal
def test_admin_get_role(portal_user_setup_teardown, dr_account_client, resp_json):

    resp = dr_account_client.admin_get_role(dr_account_client.portal_id)

    expected_resp = IS_NOT_ADMIN
    actual_resp = resp_json(resp)

    assert actual_resp == expected_resp, \
        ERROR_JSON_RESP.format(expected_resp, actual_resp)


@mark.dr_account_portal
def test_user_cannot_get_role(portal_user_setup_teardown, dr_account_client,
                              assert_status_code, auth0_token, assert_json_resp):

    resp = dr_account_client.dr_account_get_request(
        DR_ACCOUNT_ROLES_PATH,
        PORTAL_ID_QUERY_PARAM.format(portal_user_setup_teardown),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'error': 'Requires admin permissions'},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_get_role_no_portal_id(
        dr_account_client, assert_status_code, assert_json_resp):

    resp = dr_account_client.admin_get_role(portal_id=None,
                                            check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_get_role_portal_id_is_str(portal_user_setup_teardown, dr_account_client,
                                         resp_json, auth0_token, status_code, resp_text):

    resp = dr_account_client.admin_get_role(portal_id=str(dr_account_client.portal_id))

    assert resp_json(resp) == IS_NOT_ADMIN, \
        f'Did not get user role with portalId str.' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_admin_get_role_valid_non_existing_portal_id(dr_account_client, assert_json_resp,
                                                     assert_status_code):

    resp = dr_account_client.admin_get_role(portal_id=generate_uuid(),
                                            check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_update_role(portal_user_setup_teardown, dr_account_client,
                           resp_json, auth0_token):

    payload = {'portalId': dr_account_client.portal_id,
               **IS_ADMIN}
    dr_account_client.admin_update_role(payload)

    resp = dr_account_client.admin_get_role(dr_account_client.portal_id)
    actual_resp = resp_json(resp)

    assert actual_resp == IS_ADMIN, \
        ERROR_JSON_RESP.format(IS_ADMIN, actual_resp)


@mark.dr_account_portal
def test_admin_update_role_with_unknown_field(
        portal_user_setup_teardown, dr_account_client, resp_json, auth0_token):

    payload = {'portalId': dr_account_client.portal_id,
               'unknown_field': 'value',
               **IS_ADMIN}
    dr_account_client.admin_update_role(payload)

    resp = dr_account_client.admin_get_role(dr_account_client.portal_id)
    actual_resp = resp_json(resp)

    assert actual_resp == IS_ADMIN, \
        ERROR_JSON_RESP.format(IS_ADMIN, actual_resp)


@mark.dr_account_portal
def test_admin_update_to_invalid_role(portal_user_setup_teardown, dr_account_client,
                                      auth0_token, assert_status_code, assert_json_resp):

    payload = {'portalId': dr_account_client.portal_id,
               'admin': None}
    resp = dr_account_client.admin_update_role(payload,
                                               check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {'admin': 'value should be True or False'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_update_role_without_portal_id(
        dr_account_client, assert_json_resp, assert_status_code):

    resp = dr_account_client.admin_update_role(IS_ADMIN,
                                               check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_update_deleted_user_role(
        portal_user_setup, dr_account_client, auth0_token, assert_json_resp,
        assert_status_code):

    portal_id = dr_account_client.portal_id

    dr_account_client.delete_user(portal_id)

    payload = {'portalId': portal_id, **IS_ADMIN}
    resp = dr_account_client.admin_update_role(payload,
                                               check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_update_role_only_portal_id_in_payload(
        portal_user_setup_teardown, dr_account_client, auth0_token, resp_json):

    dr_account_client.admin_update_role(
        {'portalId': dr_account_client.portal_id})

    actual_resp = resp_json(
        dr_account_client.admin_get_role(dr_account_client.portal_id))

    assert actual_resp == IS_NOT_ADMIN, \
        ERROR_JSON_RESP.format(IS_NOT_ADMIN, actual_resp)


@mark.dr_account_portal
def test_update_account_non_existing_portal_id(
        dr_account_client, assert_json_resp, assert_status_code):

    resp = dr_account_client.admin_update_role(IS_ADMIN,
                                               portal_id=generate_uuid(),
                                               check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
