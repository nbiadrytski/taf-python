from pytest import mark

from utils.constants import (
    ASSERT_ERRORS,
    PORTAL_ID_REQUIRED_ERROR,
    ACCOUNT_NOT_YOURS_ERROR,
    NOT_VALID_ACCOUNT_ERROR,
    ERROR_STATUS_CODE_RESPONSE,
    DR_ACCOUNT_ACCOUNT_PATH,
    PORTAL_ID_QUERY_PARAM,
    PORTAL_ID_ERROR,
    STAGING_SELF_SERVICE_TEST_USER
)

from utils.helper_funcs import generate_uuid


LANG_ERROR_MESSAGE = 'Expected language: "{}", but got "{}" for DR Account Portal and "{}" for AutoML'
NEW_PASSWORD = 'Testing123@@@'
LANG_FR = 'fr'


@mark.dr_account_portal
def test_account_info(portal_user_setup_teardown,
                      default_account_resp,
                      dr_account_client,
                      auth0_token,
                      resp_json,
                      status_code,
                      resp_text,
                      get_user_identity):

    resp = dr_account_client.get_account(dr_account_client.portal_id)

    assert resp_json(resp) == default_account_resp(get_user_identity[0]), \
        f'Did not get user account info.' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_account_no_portal_id(portal_user_setup_teardown,
                              dr_account_client,
                              auth0_token,
                              assert_status_code,
                              assert_json_resp):

    resp = dr_account_client.get_account(portal_id=None,
                                         check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_account_portal_id_not_yours(portal_user_setup_teardown,
                                     dr_account_client,
                                     admin_portal_id,
                                     auth0_token,
                                     assert_status_code,
                                     assert_json_resp):

    resp = dr_account_client.get_account(admin_portal_id,
                                         check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_account_portal_id_is_str(dr_account_client,
                                  account_resp,
                                  admin_portal_id,
                                  resp_json,
                                  status_code,
                                  resp_text):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_ACCOUNT_PATH,
        PORTAL_ID_QUERY_PARAM.format(str(admin_portal_id)))

    assert resp_json(resp) == account_resp(STAGING_SELF_SERVICE_TEST_USER), \
        f'Did not get user account info.' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_account_valid_non_existing_portal_id(dr_account_client,
                                              assert_json_resp,
                                              assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_ACCOUNT_PATH,
        PORTAL_ID_QUERY_PARAM.format(generate_uuid()),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_cannot_get_deleted_account(portal_user_setup,
                                          dr_account_client,
                                          auth0_token,
                                          assert_json_resp,
                                          assert_status_code):

    portal_id = dr_account_client.portal_id

    dr_account_client.delete_user(portal_id)

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_ACCOUNT_PATH,
        PORTAL_ID_QUERY_PARAM.format(portal_id),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_account_password(new_user_auth0_token,
                                 dr_account_client,
                                 resp_text):

    resp = dr_account_client.update_account(
        {'portalId': dr_account_client.portal_id,
         'password': NEW_PASSWORD})

    assert resp_text(resp) == 'OK', \
        f'Did not set a new password  {NEW_PASSWORD} for user {new_user_auth0_token}.' \
        f'\nResponse: {resp_text(resp)}'


@mark.dr_account_portal
def test_update_account_language(new_user_auth0_token,
                                 dr_account_client,
                                 resp_text):

    payload = {'portalId': dr_account_client.portal_id,
               'language': LANG_FR}
    resp = dr_account_client.update_account(payload)

    assert resp_text(resp) == 'OK'


@mark.dr_account_portal
def test_update_account_password_lang(new_user_auth0_token,
                                      dr_account_client,
                                      resp_text):

    payload = {'portalId': dr_account_client.portal_id,
               'password': NEW_PASSWORD,
               'language': LANG_FR}
    resp = dr_account_client.update_account(payload)

    assert resp_text(resp) == 'OK'


@mark.dr_account_portal
def test_update_account_password_lang_otp(new_user_auth0_token,
                                          dr_account_client,
                                          resp_text):

    portal_id = dr_account_client.portal_id
    payload = {'portalId': portal_id,
               'password': NEW_PASSWORD,
               'language': LANG_FR,
               'multiFactorAuth':
                   {'otp': {'enabled': True}}}

    resp = dr_account_client.update_account(payload)

    assert resp_text(resp) == 'OK'


@mark.dr_account_portal
def test_try_to_update_account_email(portal_user_setup_teardown,
                                     dr_account_client,
                                     auth0_token,
                                     assert_status_code,
                                     assert_json_resp):

    payload = {'portalId': dr_account_client.portal_id,
               'email': 'new_email@example.com',
               'multiFactorAuth':
                   {'otp': {'enabled': False}}}

    resp = dr_account_client.update_account(payload,
                                            check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_try_to_update_account_with_unknown_field(portal_user_setup_teardown,
                                                  dr_account_client,
                                                  auth0_token,
                                                  resp_json,
                                                  get_user_identity,
                                                  account_resp):

    payload = {'portalId': dr_account_client.portal_id,
               'someField': 'some_value',
               'multiFactorAuth':
                   {'otp': {'enabled': False}}}

    dr_account_client.update_account(payload)

    assert resp_json(  # unknown field in payload update is ignored
        dr_account_client.get_account(dr_account_client.portal_id)) == account_resp(
        username=get_user_identity[0], lang=None, otp=False)


@mark.dr_account_portal
def test_update_account_without_portal_id(portal_user_setup_teardown,
                                          dr_account_client,
                                          auth0_token,
                                          assert_json_resp,
                                          assert_status_code):

    resp = dr_account_client.update_account(
        {'language': LANG_FR}, check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_not_your_account(portal_user_setup_teardown,
                                 dr_account_client,
                                 auth0_token,
                                 admin_portal_id,
                                 assert_json_resp,
                                 assert_status_code):

    payload = {'portalId': admin_portal_id,
               'language': LANG_FR}

    resp = dr_account_client.update_account(payload,
                                            check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_account_after_user_is_deleted(portal_user_setup,
                                              dr_account_client,
                                              auth0_token,
                                              assert_json_resp,
                                              assert_status_code):
    portal_id = dr_account_client.portal_id

    dr_account_client.delete_user(portal_id)

    payload = {'portalId': portal_id,
               'language': LANG_FR}
    resp = dr_account_client.update_account(payload,
                                            check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_account_only_portal_id_in_payload(portal_user_setup_teardown,
                                                  dr_account_client,
                                                  auth0_token,
                                                  resp_json,
                                                  default_account_resp,
                                                  get_user_identity):

    dr_account_client.update_account({'portalId': dr_account_client.portal_id})

    assert resp_json(
        dr_account_client.get_account(dr_account_client.portal_id)) == \
           default_account_resp(get_user_identity[0])


@mark.dr_account_portal
def test_update_account_fields_over_max_values(new_user_auth0_token,
                                               dr_account_client,
                                               assert_status_code,
                                               assert_json_resp):

    payload = {'portalId': dr_account_client.portal_id,
               # Must include at least 3 of:
               # lowercase letter, capital letter, number, symbol
               'password': 't',
               'language': 11 * 'c',  # 10 chars limit
               'multiFactorAuth':  # None, True, False
                   {'otp': {'enabled': 'Yes'}}}

    resp = dr_account_client.update_account(payload,
                                            check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {
            'language': 'String is longer than 10 characters',
            'multiFactorAuth__otp__enabled': 'value should be True or False',
            'password': 'Password must be a minimum of 8 characters'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_account_non_existing_portal_id(dr_account_client,
                                               assert_json_resp,
                                               assert_status_code):
    payload = {'portalId': generate_uuid(),
               'language': LANG_FR}

    resp = dr_account_client.dr_account_admin_patch_request(
        DR_ACCOUNT_ACCOUNT_PATH,
        payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_can_update_every_account(portal_user_setup_teardown,
                                        dr_account_client,
                                        auth0_token,
                                        resp_json,
                                        account_resp,
                                        get_user_identity):

    payload = {'portalId': dr_account_client.portal_id,
               'multiFactorAuth':
                   {'otp': {'enabled': False}}}

    dr_account_client.dr_account_admin_patch_request(DR_ACCOUNT_ACCOUNT_PATH,
                                                     payload)
    assert resp_json(dr_account_client.get_account(dr_account_client.portal_id)) == \
           account_resp(username=get_user_identity[0], lang=None, otp=False)
