from pytest import mark

from utils.helper_funcs import (
    generate_unique_email,
    generate_uuid,
    replace_chars_if_needed
)
from utils.constants import (
    DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
    EMAIL_NOT_VALID_ACCOUNT_ERROR,
    BOTH_PORTAL_ID_AND_EMAIL_ERROR,
    ASSERT_ERRORS,
    ADMIN_PERMISSIONS_ERROR,
    CANNOT_CONVERT_TO_FLOAT_ERROR,
    NOT_VALID_ACCOUNT_ERROR,
    PORTAL_ID_OR_EMAIL_REQUIRED_ERROR,
    INVALID_EMAIL_ERROR,
    NOT_STRING_ERROR,
    PORTAL_ID_INVALID_FORMAT,
    CREDIT_BALANCE_AFTER_LAST_TRANSACTION
)
from utils.data_enums import BalanceSummaryKeys


ADJUSTMENT_REASON = 'Reason 理由'
STR_501_CHARS = 'Pasture he invited mr company shyness. But when shot real her. ' \
                'Chamber her observe visited removal six sending himself boy. ' \
                'At exquisite existence if an oh dependent excellent. Are gay head need down draw. ' \
                'Misery wonder enable mutual get set oppose the uneasy. ' \
                'End why melancholy estimating her had indulgence middletons. ' \
                'Say ferrars demands besides her address. Blind going you merit few fancy their. ' \
                'Inquietude simplicity terminated she compliment remarkably few her nay. ' \
                'The weeks are ham asked her'


@mark.dr_account_portal
def test_adjust_balance_add(new_user_auth0_token, dr_account_client,
                            assert_key_in_resp,
                            get_value_from_json_response):
    value = 3
    dr_account_client.admin_adjust_balance(value, ADJUSTMENT_REASON)

    balance_resp = dr_account_client.get_balance_summary()

    errors = []
    assert_key_in_resp(
        balance_resp,
        key=BalanceSummaryKeys.BALANCE_AFTER_LAST_TRANSACTION.value,
        expected_value=CREDIT_BALANCE_AFTER_LAST_TRANSACTION,
        errors_list=errors)
    assert_key_in_resp(balance_resp,
                       key=BalanceSummaryKeys.CURRENT_BALANCE.value,
                       expected_value=value,
                       errors_list=errors)
    assert_key_in_resp(balance_resp,
                       key=BalanceSummaryKeys.RAW_BALANCE.value,
                       expected_value=value,
                       errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_add_twice(new_user_auth0_token, dr_account_client,
                                  assert_key_in_resp,
                                  get_value_from_json_response):

    user_email, _ = new_user_auth0_token
    value_1 = 2.9
    value_2 = 3.459

    dr_account_client.admin_adjust_balance(email=user_email,
                                           value=value_1,
                                           reason=ADJUSTMENT_REASON)
    dr_account_client.admin_adjust_balance(email=user_email,
                                           value=value_2,
                                           reason=ADJUSTMENT_REASON)

    balance_resp = dr_account_client.get_balance_summary(
        email=replace_chars_if_needed(user_email))

    errors = []
    assert_key_in_resp(
        balance_resp,
        key=BalanceSummaryKeys.BALANCE_AFTER_LAST_TRANSACTION.value,
        expected_value=CREDIT_BALANCE_AFTER_LAST_TRANSACTION,
        errors_list=errors)
    assert_key_in_resp(balance_resp,
                       key=BalanceSummaryKeys.CURRENT_BALANCE.value,
                       expected_value=7,
                       errors_list=errors)
    assert_key_in_resp(balance_resp,
                       key=BalanceSummaryKeys.RAW_BALANCE.value,
                       expected_value=value_1 + value_2,
                       errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_subtract(new_user_auth0_token, dr_account_client,
                                 assert_key_in_resp,
                                 get_value_from_json_response):

    user_email, _ = new_user_auth0_token
    value_1 = 5
    value_2 = -1.4

    dr_account_client.admin_adjust_balance(email=user_email,
                                           value=value_1,
                                           reason=ADJUSTMENT_REASON)
    dr_account_client.admin_adjust_balance(email=user_email,
                                           value=value_2,
                                           reason=ADJUSTMENT_REASON)

    balance_resp = dr_account_client.get_balance_summary()

    errors = []
    assert_key_in_resp(
        balance_resp,
        key=BalanceSummaryKeys.BALANCE_AFTER_LAST_TRANSACTION.value,
        expected_value=CREDIT_BALANCE_AFTER_LAST_TRANSACTION,
        errors_list=errors)
    assert_key_in_resp(balance_resp,
                       key=BalanceSummaryKeys.CURRENT_BALANCE.value,
                       expected_value=4,
                       errors_list=errors)
    assert_key_in_resp(balance_resp,
                       key=BalanceSummaryKeys.RAW_BALANCE.value,
                       expected_value=value_1 + value_2,
                       errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_try_to_adjust_balance_below_0(portal_user_setup_teardown,
                                       dr_account_client,
                                       resp_json):

    resp = dr_account_client.admin_adjust_balance(-1,
                                                  ADJUSTMENT_REASON)

    assert resp_json(resp) == {'balance': 0, 'balanceRaw': 0.0}


@mark.dr_account_portal
def test_adjust_balance_int_value_is_str(new_user_auth0_token,
                                         dr_account_client,
                                         status_code,
                                         assert_status_code,
                                         assert_json_resp):

    resp = dr_account_client.admin_adjust_balance(
        value='2',
        check_status_code=False)

    errors = []
    assert_status_code(
        resp, expected_code=201, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'balance': 2, 'balanceRaw': 2.0},
        errors_list=errors
    )

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_value_invalid_fields(dr_account_client,
                                             assert_status_code,
                                             assert_json_resp):

    resp = dr_account_client.admin_adjust_balance(
        email='invalid_email@',
        value=None,
        reason=123,
        check_status_code=False)

    errors = []
    assert_status_code(
        resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': {'email': INVALID_EMAIL_ERROR,
                                  'value': 'value is not float',
                                  'reason': NOT_STRING_ERROR}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_long_reason(portal_user_setup_teardown,
                                    dr_account_client,
                                    assert_status_code,
                                    assert_json_resp):

    resp = dr_account_client.admin_adjust_balance(
        value='two',
        reason=STR_501_CHARS,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors':
                           {'value': CANNOT_CONVERT_TO_FLOAT_ERROR,
                            'reason': 'String is longer than 500 characters'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_value_no_required_fields(dr_account_client,
                                                 assert_status_code,
                                                 assert_json_resp):

    resp = dr_account_client.dr_account_admin_put_request(
        DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
        request_body={},
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors':
                           {'portalId': PORTAL_ID_OR_EMAIL_REQUIRED_ERROR,
                            'email': PORTAL_ID_OR_EMAIL_REQUIRED_ERROR,
                            'value': 'is required',
                            'reason': 'is required'}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_non_existing_email(dr_account_client,
                                           assert_status_code,
                                           assert_json_resp):

    resp = dr_account_client.admin_adjust_balance(
        email=generate_unique_email(),
        value=1,
        reason=ADJUSTMENT_REASON,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=EMAIL_NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_value_non_existing_portal_id(dr_account_client,
                                                     assert_status_code,
                                                     assert_json_resp):
    payload = {'portalId': generate_uuid(),
               'value': 1,
               'reason': ADJUSTMENT_REASON}
    resp = dr_account_client.dr_account_admin_put_request(
        DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
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
def test_adjust_balance_value_invalid_portal_id(dr_account_client,
                                                assert_status_code,
                                                assert_json_resp):
    payload = {'portalId': 'invalid_portal_id',
               'value': 1,
               'reason': ADJUSTMENT_REASON}
    resp = dr_account_client.dr_account_admin_put_request(
        DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
        payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'errors': PORTAL_ID_INVALID_FORMAT},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_adjust_balance_both_email_and_portal_id(portal_user_setup_teardown,
                                                 dr_account_client,
                                                 assert_status_code,
                                                 get_user_identity,
                                                 assert_json_resp):

    payload = {'portalId': dr_account_client.portal_id,
               'email': get_user_identity[0],
               'value': 1,
               'reason': ADJUSTMENT_REASON}
    resp = dr_account_client.dr_account_admin_put_request(
        DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
        payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=BOTH_PORTAL_ID_AND_EMAIL_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_non_admin_cannot_adjust_balance(portal_user_setup_teardown,
                                         dr_account_client,
                                         auth0_token, assert_status_code,
                                         assert_json_resp):

    payload = {'portalId': dr_account_client.portal_id,
               'value': 1,
               'reason': ADJUSTMENT_REASON}
    resp = dr_account_client.dr_account_put_request(
        DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
        payload,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=401, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=ADMIN_PERMISSIONS_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.dr_account_portal
def test_cannot_adjust_balance_for_deleted_user(portal_user_setup,
                                                dr_account_client,
                                                auth0_token,
                                                assert_status_code,
                                                assert_json_resp):

    dr_account_client.delete_user(dr_account_client.portal_id)

    resp = dr_account_client.admin_adjust_balance(
        value=1,
        reason=ADJUSTMENT_REASON,
        check_status_code=False)

    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp=NOT_VALID_ACCOUNT_ERROR,
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
