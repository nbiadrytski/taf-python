from pytest import mark

from utils.helper_funcs import auth_header


@mark.dr_account_portal
def test_validate_auth(dr_account_client, resp_json):

    resp = dr_account_client.validate_auth(modify_header=False)
    actual_resp = resp_json(resp)

    expected_resp = {'valid': True,
                     'admin': True,
                     'creditsUser': False}

    assert actual_resp == expected_resp, \
        f'Expected response: {expected_resp}, got: {actual_resp}'


@mark.dr_account_portal
def test_validate_auth_no_auth_header(dr_account_client, resp_text, resp_json):

    resp = dr_account_client.validate_auth(modify_header=True)

    expected_resp = {'error': 'Must include \'Authorization\' header'}

    assert resp_json(resp) == expected_resp, \
        f'Expected response: {expected_resp}, got: {resp_text(resp)}'


@mark.dr_account_portal
def test_validate_auth_bad_auth_header(dr_account_client, resp_json, resp_text):

    resp = dr_account_client.validate_auth(modify_header=True,
                                           header=auth_header('invalid'))

    expected_resp = {'error': 'Invalid Bearer token'}

    assert resp_json(resp) == expected_resp, \
        f'Expected response: {expected_resp}, got: {resp_text(resp)}'
