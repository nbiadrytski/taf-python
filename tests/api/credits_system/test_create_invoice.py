from pytest import (
    mark,
    fixture
)

from utils.data_enums import (
    CreateInvoiceKeys,
    CreditPackType
)
from utils.helper_funcs import text_matches_regexp
from utils.constants import ASSERT_ERRORS


INVOICE_ID_REGEXP = 'in_[a-zA-Z0-9]{24}$'
INVOICE_URL_REGEXP = 'https://invoice.stripe.com/i/acct_[a-zA-Z0-9]{16}/test_[a-zA-Z0-9]{84}$'
INVOICE_ID_MESSAGE = 'invoiceId {} does not match regexp pattern {}'
INVOICE_URL_MESSAGE = 'invoiceUrl {} does not match regexp pattern {}'
VALID_ADDRESS = '4139 Petunia Way'
VALID_CITY = 'Birmingham'
VALID_STATE = 'AL'
VALID_POSTAL_CODE = '35208'


@mark.credits_system
@mark.trial
def test_create_explorer_invoice(
        payg_drap_user_setup_teardown, get_value_from_json_response,
        credit_packs, app_client, assert_response):

    explorer, _ = credit_packs(CreditPackType.EXPLORER.value)

    resp = app_client.v2_create_invoice(
        explorer, VALID_ADDRESS, VALID_CITY, VALID_STATE, VALID_POSTAL_CODE)

    invoice_id = get_value_from_json_response(
        resp, CreateInvoiceKeys.INVOICE_ID.value
    )
    invoice_url = get_value_from_json_response(
        resp, CreateInvoiceKeys.INVOICE_URL.value
    )

    errors = []
    assert_response(invoice_id, invoice_url, errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.credits_system
@mark.trial
def test_create_accelerator_invoice(
        payg_drap_user_setup_teardown, get_value_from_json_response,
        credit_packs, app_client, assert_response):

    accelerator, _ = credit_packs(CreditPackType.ACCELERATOR.value)

    resp = app_client.v2_create_invoice(
        accelerator, VALID_ADDRESS, VALID_CITY, VALID_STATE, VALID_POSTAL_CODE)

    invoice_id = get_value_from_json_response(
        resp, CreateInvoiceKeys.INVOICE_ID.value
    )
    invoice_url = get_value_from_json_response(
        resp, CreateInvoiceKeys.INVOICE_URL.value
    )

    errors = []
    assert_response(invoice_id, invoice_url, errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def assert_response():
    def assert_response(invoice_id, invoice_url, errors_list):

        if not text_matches_regexp(invoice_id, INVOICE_ID_REGEXP):
            errors_list.append(
                INVOICE_ID_MESSAGE.format(invoice_id, INVOICE_ID_REGEXP)
            )
        if not text_matches_regexp(invoice_url, INVOICE_URL_REGEXP):
            errors_list.append(
                INVOICE_URL_MESSAGE.format(invoice_url, INVOICE_URL_REGEXP)
            )
    return assert_response
