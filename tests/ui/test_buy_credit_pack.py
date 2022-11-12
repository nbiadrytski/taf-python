from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import ASSERT_ERRORS
from utils.ui_constants import DOWNLOADS_PATH
from utils.selectors_enums import (
    InvoiceCardPageSelectors,
    TEXT
)
from utils.data_enums import (
    CreditPackType,
    HtmlAttribute
)
from utils.helper_funcs import (
    extract_text_from_pdf,
    future_date
)


EXPLORER_PRICE = '$99.99'
ACCELERATOR_PRICE = '$499.99'
EXPLORER = 'Explorer'
ACCELERATOR = 'Accelerator'
PDF_ERROR_MESSAGE = '{file_type} {section} not in file.\n' \
                    'Expected section: "{expected_content}".' \
                    '\nFile: "{file_content}"'
INVOICE_FILE_TYPE = 'Invoice'
RECEIPT_FILE_TYPE = 'Receipt'
DR_CONTACT_DETAILS = '225 Franklin Street\n' \
                     '13th Floor\n' \
                     'Boston, Massachusetts 02110\n' \
                     'United States\n' \
                     '+1 617-765-4500\n' \
                     'trial-support@datarobot.com'
INVOICE_DETAILS_CONTENT = '{}\n{} Credit Pack\n' \
                          'Qty 1\n{}\n' \
                          'Amount due\n' \
                          '{}\nQuestions?'
PAID_INVOICE_DETAILS_CONTENT = 'To	{} {}\n' \
                               'From	DataRobot\n' \
                               'ITEMS\n' \
                               '{} Credit Pack\n' \
                               'Qty 1\n' \
                               '{}\nAmount due\n{}'


@mark.ui
@mark.skip_if_env('prod')
def test_buy_explorer_pack_staging(setup_and_sign_in_payg_user,
                                   home_page,
                                   fill_in_default_shipping_info,
                                   credits_packs_page,
                                   check_invoice_details,
                                   assert_invoice_card_content,
                                   assert_payment_card_info_filled_in,
                                   assert_invoice_is_downloaded,
                                   assert_invoice_file_content,
                                   assert_paid_invoice_card_content,
                                   check_paid_invoice_details,
                                   assert_receipt_is_downloaded,
                                   assert_receipt_file_content,
                                   browser_context_args):

    _, _, username, first_name, last_name = setup_and_sign_in_payg_user()
    # Assertion errors will be appended to this list
    errors = []

    home_page.go_to_credits_packs_modal()

    # ---------------------------------------------------------------
    # 1. Fill in shipping info at Explorer Pack
    # ---------------------------------------------------------------
    fill_in_default_shipping_info(CreditPackType.EXPLORER.value)

    # ---------------------------------------------------------------
    # 2. Proceed to invoice purchase
    # ---------------------------------------------------------------
    invoice_page, invoice_url = credits_packs_page.proceed_to_invoice()

    # ---------------------------------------------------------------
    # 3. Validate Invoice card content
    # ---------------------------------------------------------------
    assert_invoice_card_content(
        errors, invoice_page, EXPLORER_PRICE, first_name, last_name)

    # ---------------------------------------------------------------
    # 4. Validate Invoice details section
    # ---------------------------------------------------------------
    invoice_number = check_invoice_details(invoice_page, errors)

    # ---------------------------------------------------------------
    # 4. Download invoice file
    # ---------------------------------------------------------------
    invoice_file_name = assert_invoice_is_downloaded(
        errors, invoice_page, invoice_number,
        help_text='Downloaded from invoice page', paid_invoice=False)

    # ---------------------------------------------------------------
    # 5. Validate invoice file content
    # ---------------------------------------------------------------
    assert_invoice_file_content(
        errors, invoice_file_name, first_name, last_name, username,
        invoice_number, invoice_url)

    # ---------------------------------------------------------------
    # 6. Assert test payment card info is filled in
    # ---------------------------------------------------------------
    assert_payment_card_info_filled_in(errors, invoice_page)

    # ---------------------------------------------------------------
    # 7. Buy Explorer pack
    # ---------------------------------------------------------------
    invoice_page.buy_pack(EXPLORER_PRICE)

    # ---------------------------------------------------------------
    # 8. Validate paid invoice card content
    # ---------------------------------------------------------------
    assert_paid_invoice_card_content(
        errors, invoice_page, EXPLORER_PRICE, invoice_number)

    # ---------------------------------------------------------------
    # 9. Download invoice file from paid invoice/receipt page
    # ---------------------------------------------------------------
    paid_invoice_file_name = assert_invoice_is_downloaded(
        errors, invoice_page, invoice_number,
        help_text='Downloaded from receipt page', paid_invoice=True)

    # ---------------------------------------------------------------
    # 10. Validate invoice file content
    #     downloaded from paid invoice/receipt page
    # ---------------------------------------------------------------
    assert_invoice_file_content(
        errors, paid_invoice_file_name, first_name, last_name,
        username, invoice_number, invoice_url)

    # ---------------------------------------------------------------
    # 11. Validate paid invoice details
    # ---------------------------------------------------------------
    check_paid_invoice_details(
        errors, invoice_page, invoice_number, first_name, last_name)

    # ---------------------------------------------------------------
    # 12. Download receipt file
    # ---------------------------------------------------------------
    receipt_file_name = assert_receipt_is_downloaded(invoice_page)

    # ---------------------------------------------------------------
    # 13. Validate receipt file content
    # ---------------------------------------------------------------
    assert_receipt_file_content(
        errors, receipt_file_name, first_name, last_name, username,
        invoice_number)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.ui
@mark.skip_if_env('prod')
def test_buy_accelerator_pack_staging(setup_and_sign_in_payg_user,
                                      home_page,
                                      fill_in_default_shipping_info,
                                      credits_packs_page,
                                      check_invoice_details,
                                      assert_invoice_card_content,
                                      assert_payment_card_info_filled_in,
                                      assert_invoice_is_downloaded,
                                      assert_invoice_file_content,
                                      assert_paid_invoice_card_content,
                                      check_paid_invoice_details,
                                      assert_receipt_is_downloaded,
                                      assert_receipt_file_content,
                                      browser_context_args):

    _, _, username, first_name, last_name = setup_and_sign_in_payg_user()
    # Assertion errors will be appended to this list
    errors = []

    home_page.go_to_credits_packs_modal()

    # ---------------------------------------------------------------
    # 1. Fill in shipping info at ACCELERATOR Pack
    # ---------------------------------------------------------------
    fill_in_default_shipping_info(CreditPackType.ACCELERATOR.value)

    # ---------------------------------------------------------------
    # 2. Proceed to invoice purchase
    # ---------------------------------------------------------------
    invoice_page, invoice_url = credits_packs_page.proceed_to_invoice()

    # ---------------------------------------------------------------
    # 3. Validate Invoice card content
    # ---------------------------------------------------------------
    assert_invoice_card_content(
        errors, invoice_page, ACCELERATOR_PRICE, first_name, last_name)

    # ---------------------------------------------------------------
    # 4. Validate Invoice details section
    # ---------------------------------------------------------------
    invoice_number = check_invoice_details(
        invoice_page, errors, ACCELERATOR, ACCELERATOR_PRICE)

    # ---------------------------------------------------------------
    # 4. Download invoice file
    # ---------------------------------------------------------------
    invoice_file_name = assert_invoice_is_downloaded(
        errors, invoice_page, invoice_number,
        help_text='Downloaded from invoice page', paid_invoice=False)

    # ---------------------------------------------------------------
    # 5. Validate invoice file content
    # ---------------------------------------------------------------
    assert_invoice_file_content(
        errors, invoice_file_name, first_name, last_name, username,
        invoice_number, invoice_url, ACCELERATOR_PRICE, ACCELERATOR)

    # ---------------------------------------------------------------
    # 6. Assert test payment card info is filled in
    # ---------------------------------------------------------------
    assert_payment_card_info_filled_in(errors, invoice_page)

    # ---------------------------------------------------------------
    # 7. Buy Accelerator pack
    # ---------------------------------------------------------------
    invoice_page.buy_pack(ACCELERATOR_PRICE)

    # ---------------------------------------------------------------
    # 8. Validate paid invoice card content
    # ---------------------------------------------------------------
    assert_paid_invoice_card_content(
        errors, invoice_page, ACCELERATOR_PRICE, invoice_number)

    # ---------------------------------------------------------------
    # 9. Download invoice file from paid invoice/receipt page
    # ---------------------------------------------------------------
    paid_invoice_file_name = assert_invoice_is_downloaded(
        errors, invoice_page, invoice_number,
        help_text='Downloaded from receipt page', paid_invoice=True)

    # ---------------------------------------------------------------
    # 10. Validate invoice file content
    #     downloaded from paid invoice/receipt page
    # ---------------------------------------------------------------
    assert_invoice_file_content(
        errors, paid_invoice_file_name, first_name, last_name, username,
        invoice_number, invoice_url, ACCELERATOR_PRICE, ACCELERATOR)

    # ---------------------------------------------------------------
    # 11. Validate paid invoice details
    # ---------------------------------------------------------------
    check_paid_invoice_details(
        errors, invoice_page, invoice_number, first_name, last_name,
        ACCELERATOR, ACCELERATOR_PRICE)

    # ---------------------------------------------------------------
    # 12. Download receipt file
    # ---------------------------------------------------------------
    receipt_file_name = assert_receipt_is_downloaded(invoice_page)

    # ---------------------------------------------------------------
    # 13. Validate receipt file content
    # ---------------------------------------------------------------
    assert_receipt_file_content(
        errors, receipt_file_name, first_name, last_name,
        username, invoice_number, ACCELERATOR_PRICE, ACCELERATOR)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.ui
@mark.skip_if_env('staging')
def test_explorer_pack_invoice_prod(setup_and_sign_in_payg_user,
                                    home_page,
                                    fill_in_default_shipping_info,
                                    credits_packs_page,
                                    check_invoice_details,
                                    assert_invoice_card_content,
                                    assert_card_info_is_empty,
                                    assert_invoice_is_downloaded,
                                    assert_invoice_file_content,
                                    browser_context_args):

    _, _, username, first_name, last_name = setup_and_sign_in_payg_user()
    # Assertion errors will be appended to this list
    errors = []

    home_page.go_to_credits_packs_modal()

    # ---------------------------------------------------------------
    # 1. Fill in shipping info at Explorer Pack
    # ---------------------------------------------------------------
    fill_in_default_shipping_info(CreditPackType.EXPLORER.value)

    # ---------------------------------------------------------------
    # 2. Proceed to invoice purchase
    # ---------------------------------------------------------------
    invoice_page, invoice_url = credits_packs_page.proceed_to_invoice()

    # ---------------------------------------------------------------
    # 3. Validate Invoice card content
    # ---------------------------------------------------------------
    assert_invoice_card_content(
        errors, invoice_page, EXPLORER_PRICE, first_name, last_name)

    # ---------------------------------------------------------------
    # 4. Validate Invoice details section
    # ---------------------------------------------------------------
    invoice_number = check_invoice_details(invoice_page, errors)

    # ---------------------------------------------------------------
    # 4. Download invoice file
    # ---------------------------------------------------------------
    invoice_file_name = assert_invoice_is_downloaded(
        errors, invoice_page, invoice_number,
        help_text='Downloaded from invoice page', paid_invoice=False)

    # ---------------------------------------------------------------
    # 5. Validate invoice file content
    # ---------------------------------------------------------------
    assert_invoice_file_content(
        errors, invoice_file_name, first_name, last_name, username,
        invoice_number, invoice_url)

    # ---------------------------------------------------------------
    # 6. Assert payment card info is empty
    # ---------------------------------------------------------------
    assert_card_info_is_empty(errors, invoice_page)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.ui
@mark.skip_if_env('staging')
def test_accelerator_pack_invoice_prod(setup_and_sign_in_payg_user,
                                       home_page,
                                       fill_in_default_shipping_info,
                                       credits_packs_page,
                                       check_invoice_details,
                                       assert_invoice_card_content,
                                       assert_card_info_is_empty,
                                       assert_invoice_is_downloaded,
                                       assert_invoice_file_content,
                                       browser_context_args):

    _, _, username, first_name, last_name = setup_and_sign_in_payg_user()
    # Assertion errors will be appended to this list
    errors = []

    home_page.go_to_credits_packs_modal()

    # ---------------------------------------------------------------
    # 1. Fill in shipping info at ACCELERATOR Pack
    # ---------------------------------------------------------------
    fill_in_default_shipping_info(CreditPackType.ACCELERATOR.value)

    # ---------------------------------------------------------------
    # 2. Proceed to invoice purchase
    # ---------------------------------------------------------------
    invoice_page, invoice_url = credits_packs_page.proceed_to_invoice()

    # ---------------------------------------------------------------
    # 3. Validate Invoice card content
    # ---------------------------------------------------------------
    assert_invoice_card_content(
        errors, invoice_page, ACCELERATOR_PRICE, first_name, last_name)

    # ---------------------------------------------------------------
    # 4. Validate Invoice details section
    # ---------------------------------------------------------------
    invoice_number = check_invoice_details(
        invoice_page, errors, ACCELERATOR, ACCELERATOR_PRICE)

    # ---------------------------------------------------------------
    # 4. Download invoice file
    # ---------------------------------------------------------------
    invoice_file_name = assert_invoice_is_downloaded(
        errors, invoice_page, invoice_number,
        help_text='Downloaded from invoice page', paid_invoice=False)

    # ---------------------------------------------------------------
    # 5. Validate invoice file content
    # ---------------------------------------------------------------
    assert_invoice_file_content(
        errors, invoice_file_name, first_name, last_name, username,
        invoice_number, invoice_url, ACCELERATOR_PRICE, ACCELERATOR)

    # ---------------------------------------------------------------
    # 6. Assert payment card info is empty
    # ---------------------------------------------------------------
    assert_card_info_is_empty(errors, invoice_page)


@fixture
def fill_in_default_shipping_info(credits_packs_page):
    """
    Opens Credit Pack card with shipping info side.
    Fills in default shipping provided in credits_packs_page.fill_in_shipping_info()
    """
    def fill_in_shipping_info(pack_type):

        credits_packs_page.open_credit_pack_shipping_info(pack_type)
        credits_packs_page.fill_in_shipping_info(pack_type)

    return fill_in_shipping_info


@fixture
def check_invoice_details(assert_invoice_details):
    """
    Clicks 'View invoice details' button.
    Clicks 'Contact DataRobot' button at the bottom of invoice details.
    Asserts email and phone at popover which appears after the button is clicked.
    Validates invoice details section content.
    Returns invoice_number (e.g. C7B07423-0004) retrieved from invoice details header.
    Closes invoice details by clicking 'Close invoice details' button.
    """
    def invoice_details(invoice_page, errors_list, pack_name=EXPLORER,  # Explorer, Accelerator
                        pack_price=EXPLORER_PRICE):  # $99.99, $499.99

        invoice_page.view_invoice_details()
        invoice_page.check_contact_dr_from_invoice_details()
        assert_invoice_details(errors_list, invoice_page, pack_name, pack_price)
        invoice_number = invoice_page.get_invoice_number_from_invoice_details()
        invoice_page.close_invoice_details()

        return invoice_number

    return invoice_details


@fixture
def check_paid_invoice_details(assert_invoice_details, assert_element_is_present):
    """
    Clicks 'View invoice details' button from paid invoice card.
    Validates invoice details section content.
    Asserts invoice # is present at the top of invoice details section.
    Clicks 'Contact DataRobot' button at the bottom of invoice details.
    Asserts email and phone at popover which appears after the button is clicked.
    """
    def paid_invoice_details(
            errors_list, invoice_page, invoice_number, first_name, last_name,
            pack_name=EXPLORER, price=EXPLORER_PRICE):

        invoice_page.view_invoice_details()
        assert_invoice_details(
            errors_list, invoice_page, pack_name, price, first_name, last_name,
            paid_invoice=True
        )
        assert_element_is_present(
            invoice_page, InvoiceCardPageSelectors.
                PAID_INVOICE_DETAILS_INVOICE_NUMBER.value.format(invoice_number),
            errors_list, help_text='Wrong paid invoice details invoice #'
        )
        invoice_page.check_contact_dr_from_invoice_details()
        invoice_page.close_invoice_details(close_from_card=False)

    return paid_invoice_details


@fixture
def assert_invoice_details():
    """
    Validates unpaid or paid invoice details section (appears after clicking 'View invoice details' button).
    'pack_name' param: either Explorer or Accelerator.
    'price' param: e.g. '$99.99' or '$499.99'.
    """
    def invoice_details(errors_list, invoice_page, pack_name, price,
                        first_name=None, last_name=None, paid_invoice=False):

        content = invoice_page.get_inner_text(
            InvoiceCardPageSelectors.INVOICE_DETAILS_CONTENT.value
        )
        if paid_invoice:
            expected_content = PAID_INVOICE_DETAILS_CONTENT.format(
                first_name, last_name, pack_name, price, price
            )
        else:
            expected_content = INVOICE_DETAILS_CONTENT.format(
                price, pack_name, price, price
            )
        if expected_content not in content:
            errors_list.append(
                f'Expected invoice details content: "{expected_content}",'
                f' but got: "{content}"')

    return invoice_details


@fixture
def assert_invoice_is_downloaded():
    """
    Downloads invoice file either from invoice or receipt page.
    Adds error to errors_list if invoice filename doesn't contain invoice #.
    Returns invoice_file_name.
    """
    def invoice_is_downloaded(
            errors_list, invoice_page, invoice_number, help_text, paid_invoice=False):

        invoice_file_name = invoice_page.download_invoice(paid_invoice)
        if invoice_number not in invoice_file_name:
            errors_list.append(
                f'No invoice # "{invoice_number}" in file name'
                f' "{invoice_file_name}". {help_text}')

        return invoice_file_name

    return invoice_is_downloaded


@fixture
def assert_receipt_is_downloaded():
    """
    Downloads receipt file.
    Returns receipt_number retrieved from receipt file name.
    """
    def receipt_is_downloaded(invoice_page):

        receipt_file_name = invoice_page.download_receipt()

        return receipt_file_name

    return receipt_is_downloaded


@fixture
def assert_invoice_file_content(validate_invoice_file):
    """
    Extracts text from invoice .pdf file.
    Validates extracted invoice content.
    """
    def invoice_file_content(errors_list, invoice_file_name,
                             first_name, last_name, username,
                             invoice_number, invoice_url,
                             price=EXPLORER_PRICE, pack_name=EXPLORER):

        content = extract_text_from_pdf(f'{DOWNLOADS_PATH}/{invoice_file_name}')
        validate_invoice_file(
            errors_list, content, first_name, last_name, username,
            invoice_number, invoice_url, price, pack_name)

    return invoice_file_content


@fixture
def assert_receipt_file_content(validate_receipt_file):
    """
    Extracts text from receipt .pdf file.
    Retrieves receipt # from file name.
    Validates extracted receipt content.
    """
    def receipt_file_content(
            errors_list, receipt_file_name, first_name, last_name,
            username, invoice_number, price=EXPLORER_PRICE, pack_name=EXPLORER):

        content = extract_text_from_pdf(f'{DOWNLOADS_PATH}/{receipt_file_name}')
        validate_receipt_file(
            errors_list, content, first_name, last_name, username,
            invoice_number, price, pack_name)

    return receipt_file_content


@fixture
def validate_invoice_file():
    """Validates content of downloaded invoice .pdf file"""

    def invoice_file(
            errors_list, file_content, first_name, last_name, username,
            invoice_number, invoice_url, price, pack_name):

        if DR_CONTACT_DETAILS not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=INVOICE_FILE_TYPE, section='"DR Contact details"',
                    expected_content=DR_CONTACT_DETAILS, file_content=file_content))

        invoice_details = InvoicePdf.INVOICE_DETAILS.value.format(
            number=invoice_number, today=future_date(days=0, long_month=False),
            tomorrow=future_date(days=1, long_month=False))
        # there may be some flakiness introduced by Stripe invoice processing date
        # and purchase date timestamp done while the test was running
        invoice_details_plus_one_day = InvoicePdf.INVOICE_DETAILS.value.format(
            number=invoice_number, today=future_date(days=1, long_month=False),
            tomorrow=future_date(days=2, long_month=False)
        )
        if invoice_details not in file_content:
            if invoice_details_plus_one_day not in file_content:
                errors_list.append(
                    PDF_ERROR_MESSAGE.format(
                        file_type=INVOICE_FILE_TYPE, section='"Invoice details"',
                        expected_content=f'"{invoice_details}" or "{invoice_details_plus_one_day}"',
                        file_content=file_content))

        user_info = InvoicePdf.USER_IFO.value.format(first_name, last_name, username)
        if user_info not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=INVOICE_FILE_TYPE, section='"User info"',
                    expected_content=user_info, file_content=file_content))

        price_header = InvoicePdf.PRICE_HEADER.value.format(
            price=price, date=future_date(days=1, long_month=True))
        # there may be some flakiness introduced by Stripe invoice processing date
        # and purchase date timestamp done while the test was running
        price_header_plus_day = InvoicePdf.PRICE_HEADER.value.format(
            price=price, date=future_date(days=2, long_month=True)
        )
        if price_header not in file_content:
            if price_header_plus_day not in file_content:
                errors_list.append(
                    PDF_ERROR_MESSAGE.format(
                        file_type=INVOICE_FILE_TYPE, section='Price header',
                        expected_content=f'"{price_header}" or "{price_header_plus_day}"',
                        file_content=file_content))

        if pack_name == ACCELERATOR:
            if InvoicePdf.ACCEL_PRICE_TABLE.value not in file_content:
                errors_list.append(
                    PDF_ERROR_MESSAGE.format(
                        file_type=INVOICE_FILE_TYPE, section='Table columns and values',
                        expected_content=InvoicePdf.ACCEL_PRICE_TABLE.value,
                        file_content=file_content))

        pay_with_card = InvoicePdf.PAY_WITH_CARD.value.format(price)
        if pay_with_card not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=INVOICE_FILE_TYPE, section='Pay with card section',
                    expected_content=pay_with_card, file_content=file_content))

        visit_url = InvoicePdf.VISIT_URL.value.format(invoice_url)
        if visit_url not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=INVOICE_FILE_TYPE, section='Visit url',
                    expected_content=visit_url, file_content=file_content))

    return invoice_file


@fixture
def validate_receipt_file():
    """Validates content of downloaded receipt .pdf file"""

    def receipt_file(
            errors_list, file_content, first_name, last_name, username,
            invoice_number, price, pack_name, card_last_four_digits='4242'):

        if DR_CONTACT_DETAILS not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=RECEIPT_FILE_TYPE, section='DR Contact details',
                    expected_content=DR_CONTACT_DETAILS, file_content=file_content))

        if invoice_number not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=RECEIPT_FILE_TYPE, section='Invoice #',
                    expected_content=invoice_number, file_content=file_content))

        if card_last_four_digits not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=RECEIPT_FILE_TYPE, section='Card last 4 digits',
                    expected_content=card_last_four_digits, file_content=file_content))

        user_info = ReceiptPdf.USER_IFO.value.format(first_name, last_name, username)
        if user_info not in file_content:
            errors_list.append(
                PDF_ERROR_MESSAGE.format(
                    file_type=RECEIPT_FILE_TYPE, section='"User info"',
                    expected_content=user_info, file_content=file_content))

        price_header = ReceiptPdf.PRICE_HEADER.value.format(
            price=price, date=future_date(days=0, long_month=True))
        # there may be some flakiness introduced by Stripe invoice processing date
        # and purchase date timestamp while the test was running
        price_header_plus_day = ReceiptPdf.PRICE_HEADER.value.format(
            price=price, date=future_date(days=1, long_month=True)
        )
        if price_header not in file_content:
            if price_header_plus_day not in file_content:
                errors_list.append(
                    PDF_ERROR_MESSAGE.format(
                        file_type=RECEIPT_FILE_TYPE, section='Price header',
                        expected_content=f'"{price_header}" or "{price_header_plus_day}"',
                        file_content=file_content))

        if pack_name == ACCELERATOR:
            if ReceiptPdf.ACCEL_PRICE_TABLE.value not in file_content:
                errors_list.append(
                    PDF_ERROR_MESSAGE.format(
                        file_type=RECEIPT_FILE_TYPE, section='Table columns and values',
                        expected_content=ReceiptPdf.ACCEL_PRICE_TABLE.value,
                        file_content=file_content))

    return receipt_file


@fixture
def assert_invoice_card_content():
    """
    Validates Invoice card content:
    1. Price, e.g. $99.99
    2. Due date (tomorrow) in format April 24, 2021
    3. To first_name last_name
    4. Invoice icon to download invoice
    5. Download button in bottom right corner of invoice download icon
    6. From DataRobot
    """
    def invoice_card_content(
            errors_list, invoice_page, price, first_name, last_name):

        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.CARD_PRICE.value.format(price)):
            errors_list.append(
                f'Wrong invoice card price. Expected: {price}.'
            )
        tomorrow = future_date(days=1)
        # there may be some flakiness introduced by Stripe invoice processing date
        # and purchase date timestamp while the test was running
        day_after_tomorrow = future_date(days=2)
        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.CARD_DATE.value.format(tomorrow)):
            if not invoice_page.is_element_present(
                    InvoiceCardPageSelectors.CARD_DATE.value.format(day_after_tomorrow)
            ):
                errors_list.append(
                    f'Wrong invoice card date. '
                    f'Expected: "{tomorrow}" or "{day_after_tomorrow}".'
                )
        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.CARD_INVOICE_DOWNLOAD_ICON.value):
            errors_list.append(
                'Invoice card download icon is missing.'
            )
        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.CARD_INVOICE_DOWNLOAD_BUTTON.value):
            errors_list.append(
                'Invoice card download button is missing.'
            )
        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.CARD_FIRST_LAST_NAME.value.format(
                    first_name, last_name)):
            errors_list.append(
                f'Invoice card has wrong first/last name. '
                f'Expected: {first_name} {last_name}'
            )
        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.CARD_FROM.value):
            errors_list.append(
                'Invoice card FROM value is wrong.')

    return invoice_card_content


@fixture
def assert_payment_card_info_filled_in():
    """
    Asserts if payment card info (card number, expiration date and cvc number)
    is filled in at Stripe invoice page.
    """
    def payment_card_info_filled_in(errors_list, invoice_page,
                                    card_number='4242 4242 4242 4242',
                                    expiration='12 / 22',
                                    cvc='123'):

        actual_card_number = invoice_page.get_attribute_value(
            InvoiceCardPageSelectors.CARD_NUMBER_FIELD.value,
            HtmlAttribute.VALUE.value
        )
        actual_expiration = invoice_page.get_attribute_value(
            InvoiceCardPageSelectors.CARD_EXPIRY_FIELD.value,
            HtmlAttribute.VALUE.value
        )
        actual_cvc = invoice_page.get_attribute_value(
            InvoiceCardPageSelectors.CARD_CVC_FIELD.value,
            HtmlAttribute.VALUE.value)

        error_message = 'Wrong card {}. Expected: "{}", got: "{}"'
        if actual_card_number != card_number:
            errors_list.append(
                error_message.format(
                    'number', card_number, actual_card_number)
            )
        if actual_expiration != expiration:
            errors_list.append(
                error_message.format(
                    'expiration', expiration, actual_expiration)
            )
        if actual_cvc != cvc:
            errors_list.append(
                error_message.format('cvc', cvc, actual_cvc))

    return payment_card_info_filled_in


@fixture
def assert_card_info_is_empty():
    """Asserts if payment card info (card number, expiration date and cvc number) is empty."""

    def card_info_is_empty(errors_list, invoice_page):

        actual_card_number = invoice_page.get_attribute_value(
            InvoiceCardPageSelectors.CARD_NUMBER_FIELD.value,
            HtmlAttribute.VALUE.value
        )
        actual_expiration = invoice_page.get_attribute_value(
            InvoiceCardPageSelectors.CARD_EXPIRY_FIELD.value,
            HtmlAttribute.VALUE.value
        )
        actual_cvc = invoice_page.get_attribute_value(
            InvoiceCardPageSelectors.CARD_CVC_FIELD.value,
            HtmlAttribute.VALUE.value)

        empty = ''
        error_message = 'Card {} is not empty. Got: "{}"'
        if actual_card_number != empty:
            errors_list.append(
                error_message.format('number', actual_card_number))
        if actual_expiration != empty:
            errors_list.append(
                error_message.format('expiration', actual_expiration))
        if actual_cvc != empty:
            errors_list.append(error_message.format('cvc', actual_cvc))

    return card_info_is_empty


@fixture
def assert_paid_invoice_card_content():
    """
    Validates paid invoice card content:
    1. Thumbnail image
    2. Due date (tomorrow) in format April 24, 2021
    3. To first_name last_name
    4. Invoice icon to download invoice
    5. Download button in bottom right corner of invoice download icon
    6. From DataRobot
    """
    def paid_invoice_card_content(
            errors_list, invoice_page, price, invoice_number,
            pay_method='Visa •••• 4242'):

        thumb_message = 'Paid invoice card thumbnail {} is missing'
        wrong_message = 'Wrong paid invoice card {}. Expected: "{}".'

        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.PAID_INVOICE_CARD_THUMBNAIL.value):
            errors_list.append(thumb_message.format('image'))

        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.
                        PAID_INVOICE_CARD_THUMBNAIL_SUCCESS_ICON.value):
            errors_list.append(thumb_message.format('success icon'))

        if not invoice_page.is_element_present(TEXT.format(price)):
            errors_list.append(wrong_message.format('price', price))

        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.
                        PAID_INVOICE_CARD_TABLE.value.format(invoice_number)):
            errors_list.append(
                wrong_message.format('invoice number', invoice_number))

        today_long_month = future_date(days=0, long_month=True)
        # there may be some flakiness introduced by Stripe invoice processing date
        # and purchase date timestamp while the test was running
        today_long_month_plus_day = future_date(days=1, long_month=True)
        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.
                        PAID_INVOICE_CARD_TABLE.value.format(today_long_month)):
            if not invoice_page.is_element_present(
                    InvoiceCardPageSelectors.
                            PAID_INVOICE_CARD_TABLE.value.format(today_long_month_plus_day)):
                errors_list.append(
                    wrong_message.format(
                        'payment date', f'"{today_long_month}" or "{today_long_month_plus_day}"'))

        if not invoice_page.is_element_present(
                InvoiceCardPageSelectors.
                        PAID_INVOICE_CARD_TABLE.value.format(pay_method)):
            errors_list.append(
                wrong_message.format('pay method', pay_method))

    return paid_invoice_card_content


class InvoicePdf(Enum):
    """Invoice .pdf file content divided into logical parts"""

    INVOICE_DETAILS = 'Invoice number {number}\n' \
                      '{today}\n' \
                      'Date of issue\n' \
                      '{tomorrow}\n' \
                      'Date due'
    USER_IFO = '{} {}\n{}'
    PRICE_HEADER = '{price} due {date}'
    ACCEL_PRICE_TABLE = 'Description\n\n' \
                        'Qty\n\n' \
                        'Unit price\n\n' \
                        'Accelerator Credit Pack\n\n' \
                        '1\n\n' \
                        '$499.99\n\n' \
                        'Amount\n\n' \
                        '$499.99\n\n' \
                        '$499.99\n\n' \
                        '$499.99\n\n' \
                        'Subtotal\n\n' \
                        'Amount due'
    PAY_WITH_CARD = 'Pay {} with card'
    VISIT_URL = 'Visit {}'


class ReceiptPdf(Enum):
    """Receipt .pdf file content divided into logical parts"""

    USER_IFO = '{} {}\n{}'
    PRICE_HEADER = '{price} paid on {date}'
    ACCEL_PRICE_TABLE = 'Description\n\n' \
                        'Qty\n\n' \
                        'Unit price\n\n' \
                        'Accelerator Credit Pack\n\n' \
                        '1\n\n' \
                        '$499.99\n\n' \
                        'Amount\n\n' \
                        '$499.99\n\n' \
                        '$499.99\n\n' \
                        '$499.99\n\n' \
                        'Subtotal\n\n' \
                        'Amount paid'
