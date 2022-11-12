from pytest import mark

from utils.helper_funcs import generate_unique_email
from utils.constants import (
    ASSERT_ERRORS,
    ERROR_STATUS_CODE_RESPONSE,
    DR_ACCOUNT_PORTAL_REGISTER_PATH,
    ADMIN_PERMISSIONS_ERROR,
    INVALID_EMAIL_ERROR
)


FIRST_NAME = 'Имя 名前'
LAST_NAME = 'Фамилия 苗字'

INVALID_EMAILS = ['@test.com',
                  'test.com',
                  'test$test.com',
                  'test@',
                  'test@test',
                  'test@test.',
                  '名前@test.com']


@mark.dr_account_portal
def test_register_valid_email_with_ascii_chars(
        dr_account_client, status_code, resp_json, resp_text,
        success_register_resp, portal_user_teardown):

    email = generate_unique_email('!#$%&\'''*+-/=?^_`{|}~')

    resp = dr_account_client.register_user(username=email,
                                           first_name=FIRST_NAME,
                                           last_name=LAST_NAME)

    assert resp_json(resp) == success_register_resp(), \
        f'Did not register user with email {email}' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_register_required_fields_only(
        dr_account_client, status_code, resp_json,
        resp_text, success_register_resp, portal_user_teardown):

    resp = dr_account_client.register_user(username=generate_unique_email(),
                                           first_name=FIRST_NAME,
                                           last_name=LAST_NAME)

    assert resp_json(resp) == success_register_resp(), \
        f'Did not register user with only required fields in payload.' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_register_dr_account_updated_true(user_setup_and_teardown, status_code,
                                          resp_json, resp_text, success_register_resp):

    _, _, resp = user_setup_and_teardown

    assert resp_json(resp) == success_register_resp(dr_account_updated=True), \
        f'Did not register user both to Trial and DR Account Portal. ' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_register_all_fields(
        dr_account_client, status_code, resp_json, resp_text,
        success_register_resp, portal_user_teardown):

    resp = dr_account_client.register_user(username=generate_unique_email(),
                                           first_name=FIRST_NAME,
                                           last_name=LAST_NAME,
                                           add_profile_info=True,
                                           add_social_info=True)

    assert resp_json(resp) == success_register_resp(), \
        f'Did not register user with both required and optional fields in payload.' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_register_no_required_fields(
        dr_account_client, assert_status_code, assert_json_resp):

    resp = dr_account_client.admin_register(payload={})

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {
                        'email': 'is required',
                        'firstName': 'is required',
                        'lastName': 'is required'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_invalid_request_data(
        dr_account_client, assert_status_code, assert_json_resp):

    payload = {'email': 'test@.test',
               'firstName': FIRST_NAME,
               'lastName': LAST_NAME}

    resp = dr_account_client.admin_register(payload)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': 'Invalid request data'},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
@mark.parametrize('email', INVALID_EMAILS, ids=INVALID_EMAILS)
def test_register_invalid_email(
        dr_account_client, assert_status_code, assert_json_resp, email):

    payload = {'email': email,
               'firstName': FIRST_NAME,
               'lastName': LAST_NAME}

    resp = dr_account_client.admin_register(payload)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {'email': INVALID_EMAIL_ERROR}},
        errors_list=errors,
        add_text='with invalid email ' + email + ' in payload')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_cannot_register_twice(dr_account_client, assert_status_code,
                               assert_json_resp, portal_user_teardown):

    email = generate_unique_email()

    resp1 = dr_account_client.register_user(username=email,
                                            first_name=FIRST_NAME,
                                            last_name=LAST_NAME)
    payload = {'email': email,
               'firstName': FIRST_NAME,
               'lastName': LAST_NAME}
    resp2 = dr_account_client.admin_register(payload)

    errors = []
    assert_status_code(resp1, expected_code=200, errors_list=errors)
    assert_json_resp(
        resp1,
        expected_resp={'portalId': dr_account_client.portal_id,
                       'dr_account_updated': False},
        errors_list=errors,
        add_text='after registering 1st time')

    assert_status_code(resp2, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp2,
        expected_resp={'errors': {'email': 'email is already registered'}},
        errors_list=errors,
        add_text='after registering 2nd time')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_fields_max_values(dr_account_client, resp_json, resp_text, status_code,
                           success_register_resp, portal_user_teardown):

    chars_255 = 255*'c'
    url_255_chars = 'https://test.com' + 239*'c'

    resp = dr_account_client.register_user(username=generate_unique_email(206*'m'),
                                           first_name=chars_255,
                                           last_name=chars_255,
                                           lang=10*'c',
                                           phone=20*'1',
                                           company=chars_255,
                                           industry='insurance',
                                           country='US',
                                           state='FL',
                                           linkedin=url_255_chars,
                                           github=url_255_chars,
                                           kaggle=url_255_chars,
                                           add_profile_info=True,
                                           add_social_info=True)

    assert resp_json(resp) == success_register_resp(), \
        f'Did not register user to DataRobot Account Portal. ' + \
        ERROR_STATUS_CODE_RESPONSE.format(status_code(resp), resp_text(resp))


@mark.dr_account_portal
def test_fields_exceed_max_values(dr_account_client, assert_status_code, assert_json_resp,
                                  profile_fields_over_limits, fields_limits):

    payload = profile_fields_over_limits(dr_account_client.portal_id, profile_route=False)

    resp = dr_account_client.admin_register(payload)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=fields_limits,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_delete_user_and_register_again(dr_account_client, assert_status_code,
                                        assert_json_resp, success_register_resp,
                                        portal_user_teardown):
    email = generate_unique_email()

    resp1 = dr_account_client.register_user(username=email,
                                            first_name=FIRST_NAME,
                                            last_name=LAST_NAME)

    errors = []
    assert_status_code(resp1, expected_code=200, errors_list=errors)
    assert_json_resp(
        resp1,
        expected_resp=success_register_resp(),
        errors_list=errors,
        add_text='after registering 1st time')

    dr_account_client.delete_user(dr_account_client.portal_id)

    resp2 = dr_account_client.register_user(username=email,
                                            first_name=FIRST_NAME,
                                            last_name=LAST_NAME)

    assert_status_code(resp2, expected_code=200, errors_list=errors)
    assert_json_resp(
        resp2,
        expected_resp=success_register_resp(),
        errors_list=errors,
        add_text='after deleting user and registering again')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_non_admin_cannot_register(portal_user_setup_teardown, dr_account_client,
                                   auth0_token, assert_status_code, assert_json_resp):

    payload = {'email': generate_unique_email(),
               'firstName': FIRST_NAME,
               'lastName': LAST_NAME}
    resp = dr_account_client.dr_account_post_request(DR_ACCOUNT_PORTAL_REGISTER_PATH,
                                                     payload,
                                                     check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ADMIN_PERMISSIONS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
