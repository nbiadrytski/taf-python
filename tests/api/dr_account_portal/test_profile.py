from pytest import mark

from utils.constants import (
    ASSERT_ERRORS,
    ERROR_JSON_RESP,
    DR_ACCOUNT_PROFILE_PATH,
    ERROR_STATUS_CODE_RESPONSE,
    PORTAL_ID_REQUIRED_ERROR,
    ACCOUNT_NOT_YOURS_ERROR,
    PORTAL_ID_QUERY_PARAM,
    PORTAL_ID_ERROR,
    NOT_VALID_ACCOUNT_ERROR
)
from utils.helper_funcs import generate_uuid
from utils.data_enums import (
    DrapProfileKeys,
    UserRole,
    LearningTrack
)


NEW_LAST_NAME = 'New_Last_Name'
NEW_FIRST_NAME = 'New_First_Name'


@mark.dr_account_portal
def test_profile_info(portal_user_setup_teardown, default_register_resp,
                      dr_account_client, resp_json, auth0_token,
                      status_code, resp_text):

    resp = dr_account_client.get_profile(
        portal_id=dr_account_client.portal_id)

    assert resp_json(resp) == default_register_resp, \
        f'Did not get user profile info.' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp),
                                          resp_text(resp))


@mark.dr_account_portal
def test_profile_no_portal_id(portal_user_setup_teardown,
                              dr_account_client,
                              auth0_token, assert_status_code,
                              assert_json_resp):

    resp = dr_account_client.get_profile(
        portal_id=None,
        check_status_code=False)

    errors = []
    assert_status_code(resp,
                       expected_code=400,
                       errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_profile_portal_id_not_yours(portal_user_setup_teardown,
                                     dr_account_client, auth0_token,
                                     admin_portal_id, assert_status_code,
                                     assert_json_resp):

    resp = dr_account_client.get_profile(portal_id=str(admin_portal_id),
                                         check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_cannot_get_deleted_profile(portal_user_setup,
                                          dr_account_client,
                                          auth0_token,
                                          assert_json_resp,
                                          assert_status_code):

    portal_id = dr_account_client.portal_id

    dr_account_client.delete_user(portal_id)

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_PROFILE_PATH,
        PORTAL_ID_QUERY_PARAM.format(portal_id),
        check_status_code=False)

    errors = []
    assert_status_code(resp,
                       expected_code=400,
                       errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_profile_valid_non_existing_portal_id(dr_account_client,
                                              assert_json_resp,
                                              assert_status_code):

    resp = dr_account_client.dr_account_admin_get_request(
        DR_ACCOUNT_PROFILE_PATH,
        PORTAL_ID_QUERY_PARAM.format(generate_uuid()),
        check_status_code=False)

    errors = []
    assert_status_code(resp,
                       expected_code=400,
                       errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_all_profile_fields(new_user_auth0_token,
                                   dr_account_client,
                                   resp_json, resp_text):

    payload = {'portalId': dr_account_client.portal_id,
               'firstName': NEW_FIRST_NAME,
               'lastName': NEW_LAST_NAME,
               'phoneNumber': 'New',
               'company': 'New',
               'learningTrack': LearningTrack.ML_DEVELOPMENT.value,
               'role': UserRole.BUSINESS_ANALYST.value,
               'socialProfiles':
                   {'linkedin': 'https://test-l.com/new',
                    'kaggle': 'https://test-k.com/new',
                    'github': 'https://test-g.com/new'},
               'industry': 'insurance',
               'country': 'US',
               'state': 'TX'}
    dr_account_client.update_profile(payload)

    resp = dr_account_client.get_profile(
        dr_account_client.portal_id)

    # portalId should not be in profile info
    del payload['portalId']

    assert resp_json(resp) == payload, \
        ERROR_JSON_RESP.format(
            'after updating profile', payload, resp_text(resp))


@mark.dr_account_portal
def test_update_one_profile_field(portal_user_setup_teardown,
                                  dr_account_client,
                                  auth0_token, resp_text,
                                  get_value_from_json_response,
                                  status_code):

    payload = {'portalId': dr_account_client.portal_id,
               'firstName': NEW_FIRST_NAME}

    dr_account_client.update_profile(payload)

    resp = dr_account_client.get_profile(dr_account_client.portal_id)

    assert get_value_from_json_response(
        resp, DrapProfileKeys.NAME.value) == NEW_FIRST_NAME, \
        f'firstName was not updated to {NEW_FIRST_NAME}. ' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp),
                                          resp_text(resp))


@mark.dr_account_portal
def test_update_profile_without_portal_id(portal_user_setup_teardown,
                                          dr_account_client, auth0_token,
                                          assert_json_resp,
                                          assert_status_code):

    resp = dr_account_client.update_profile(
        {'firstName': NEW_FIRST_NAME}, check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_REQUIRED_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_not_your_profile(portal_user_setup_teardown,
                                 dr_account_client,
                                 auth0_token, assert_json_resp,
                                 admin_portal_id,
                                 assert_status_code):

    payload = {'portalId': admin_portal_id,
               'firstName': NEW_FIRST_NAME}

    resp = dr_account_client.update_profile(
        payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp,
                       expected_code=401,
                       errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ACCOUNT_NOT_YOURS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_profile_unknown_field_in_payload(portal_user_setup_teardown,
                                                 dr_account_client,
                                                 auth0_token, resp_text,
                                                 get_value_from_json_response,
                                                 status_code):

    payload = {'portalId': dr_account_client.portal_id,
               'lastName': NEW_LAST_NAME,
               'name': 'New'}

    dr_account_client.update_profile(payload)

    resp = dr_account_client.get_profile(dr_account_client.portal_id)

    assert get_value_from_json_response(
        resp, DrapProfileKeys.LAST_NAME.value) == NEW_LAST_NAME, \
        f'lastName was not updated to {NEW_LAST_NAME}. ' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp),
                                          resp_text(resp))


@mark.dr_account_portal
def test_update_profile_after_user_is_deleted(portal_user_setup,
                                              dr_account_client,
                                              auth0_token,
                                              assert_json_resp,
                                              assert_status_code):

    portal_id = dr_account_client.portal_id

    dr_account_client.delete_user(portal_id)

    payload = {'portalId': portal_id,
               'lastName': NEW_LAST_NAME}

    resp = dr_account_client.update_profile(
        payload, check_status_code=False)

    errors = []
    assert_status_code(resp,
                       expected_code=401,
                       errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=PORTAL_ID_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_profile_only_portal_id_in_payload(portal_user_setup_teardown,
                                                  dr_account_client,
                                                  auth0_token, resp_json,
                                                  default_register_resp):

    dr_account_client.update_profile(
        {'portalId': dr_account_client.portal_id})

    assert resp_json(
        dr_account_client.get_profile(
            dr_account_client.portal_id)) == default_register_resp


@mark.dr_account_portal
def test_update_profile_fields_over_max_values(portal_user_setup_teardown,
                                               default_register_resp,
                                               dr_account_client,
                                               auth0_token, assert_json_resp,
                                               fields_limits, assert_status_code,
                                               profile_fields_over_limits):

    resp = dr_account_client.update_profile(
        profile_fields_over_limits(dr_account_client.portal_id),
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)

    # email and language keys are absent in profile info response
    del fields_limits['errors']['email']
    del fields_limits['errors']['language']

    assert_json_resp(
        resp,
        expected_resp=fields_limits,
        errors_list=errors,
        add_text=f'for PATCH {DR_ACCOUNT_PROFILE_PATH}')

    resp = dr_account_client.get_profile(dr_account_client.portal_id)

    assert_json_resp(
        resp,
        expected_resp=default_register_resp,
        errors_list=errors,
        add_text=f'for GET {DR_ACCOUNT_PROFILE_PATH} fields over max values')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_update_profile_non_existing_portal_id(dr_account_client,
                                               assert_json_resp,
                                               assert_status_code):

    payload = {'portalId': generate_uuid(),
               'firstName': NEW_FIRST_NAME}

    resp = dr_account_client.dr_account_admin_patch_request(
        DR_ACCOUNT_PROFILE_PATH,
        payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp,
                       expected_code=400,
                       errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_admin_can_update_every_profile(portal_user_setup_teardown,
                                        dr_account_client, auth0_token,
                                        resp_text, status_code,
                                        get_value_from_json_response):

    payload = {'portalId': dr_account_client.portal_id,
               'lastName': NEW_LAST_NAME}
    dr_account_client.dr_account_admin_patch_request(
        DR_ACCOUNT_PROFILE_PATH,
        payload)

    resp = dr_account_client.get_profile(dr_account_client.portal_id)

    assert get_value_from_json_response(
        resp, DrapProfileKeys.LAST_NAME.value) == NEW_LAST_NAME, \
        f'lastName was not updated to {NEW_LAST_NAME}. ' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp),
                                          resp_text(resp))
