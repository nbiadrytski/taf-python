from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import ASSERT_ERRORS
from utils.selectors_enums import TEXT
from utils.data_enums import (
    CreditPackType,
    HtmlAttribute
)


@mark.ui
@mark.skip_if_env('prod')
def test_credit_pack_shipping_info_validation(
        setup_and_sign_in_payg_user, home_page, credits_packs_page,
        assert_element_is_not_present, validate_field,
        validate_cleared_field, assert_proceed_button_is_enabled
):
    setup_and_sign_in_payg_user()
    # Assertion errors will be appended to this list
    errors = []

    home_page.go_to_credits_packs_modal()
    credits_packs_page.open_credit_pack_shipping_info(
        CreditPackType.ACCELERATOR.value)

    # -------------------------------------------------------------------------
    # 1. Zip Code cannot contain invalid symbols
    # -------------------------------------------------------------------------
    zip_value = '123'
    credits_packs_page.fill_in_zip_code_field(
        CreditPackType.ACCELERATOR.value, zip_value)
    validate_field(
        errors_list=errors,
        pack_name=CreditPackType.ACCELERATOR.value, value=zip_value,
        validation_message_selector=ValidationMessageSelectors.ZIP_CODE.value,
        field_name=ZIP, field_element=credits_packs_page.accel_zip_field,
        help_text=ENTER_INTO_FIELD.format(zip_value, ZIP))

    # -------------------------------------------------------------------------
    # 2. Accelerator State Address validation message disappears
    #    when opening Explorer
    # -------------------------------------------------------------------------
    credits_packs_page.open_credit_pack_shipping_info(
        CreditPackType.EXPLORER.value)
    assert_element_is_not_present(
        credits_packs_page, ValidationMessageSelectors.STATE_ADDRESS.value,
        errors,
        f'{ValidationMessageSelectors.STATE_ADDRESS.value} validation error '
        f'must be absent after opening Explorer card.')

    # -------------------------------------------------------------------------
    # 3. Fill in Explorer fields with valid values. 'Proceed' button is enabled.
    # -------------------------------------------------------------------------
    credits_packs_page.fill_in_shipping_info(CreditPackType.EXPLORER.value)

    # -------------------------------------------------------------------------
    # 4. Validate Street Address field after clearing it.
    #    'Please fill in all the required fields' validation message
    # -------------------------------------------------------------------------
    credits_packs_page.fill_in_street_address_field(
        CreditPackType.EXPLORER.value, '')
    validate_cleared_field(
        errors_list=errors, pack_name=CreditPackType.EXPLORER.value,
        validation_message_selector=ValidationMessageSelectors.
            REQUIRED_FIELDS.value,
        field_name=STREET_ADDRESS,
        field_element=credits_packs_page.explorer_street_address_field,
        help_text=CLEAR_FIELD.format(STREET_ADDRESS))

    # -------------------------------------------------------------------------
    # 5. 'Proceed' button gets enabled after filling in Street Address field
    #    back with valid value.
    # -------------------------------------------------------------------------
    valid_street = '4139 Petunia Way'
    credits_packs_page.fill_in_street_address_field(
        CreditPackType.EXPLORER.value, valid_street)
    assert_proceed_button_is_enabled(
        errors, CreditPackType.EXPLORER.value,
        help_text=FILL_BACK_MESSAGE.format(STREET_ADDRESS))

    # -------------------------------------------------------------------------
    # 6. Validate City field after clearing it.
    #    'Please fill in all the required fields' validation message
    # -------------------------------------------------------------------------
    credits_packs_page.fill_in_city_field(CreditPackType.EXPLORER.value, '')
    validate_cleared_field(
        errors_list=errors, pack_name=CreditPackType.EXPLORER.value,
        validation_message_selector=ValidationMessageSelectors.
            REQUIRED_FIELDS.value,
        field_name=CITY, field_element=credits_packs_page.explorer_city_field,
        help_text=CLEAR_FIELD.format(CITY))

    # -------------------------------------------------------------------------
    # 7. 'Proceed' button gets enabled after filling in City field back
    #    with valid value
    # -------------------------------------------------------------------------
    valid_city = 'Mobile'
    credits_packs_page.fill_in_city_field(
        CreditPackType.EXPLORER.value, valid_city)
    assert_proceed_button_is_enabled(
        errors, CreditPackType.EXPLORER.value,
        help_text=FILL_BACK_MESSAGE.format(CITY))

    # -------------------------------------------------------------------------
    # 8. Validate Zip Code field after clearing it.
    #     'Please fill in all the required fields' validation message
    # -------------------------------------------------------------------------
    credits_packs_page.fill_in_zip_code_field(
        CreditPackType.EXPLORER.value, '')
    validate_cleared_field(
        errors_list=errors, pack_name=CreditPackType.EXPLORER.value,
        validation_message_selector=ValidationMessageSelectors.
            REQUIRED_FIELDS.value,
        field_name=ZIP, field_element=credits_packs_page.explorer_zip_field,
        help_text=CLEAR_FIELD.format(ZIP))

    # -------------------------------------------------------------------------
    # 9. 'Proceed' button gets enabled after filling in Zip Code field
    #      back with valid value.
    # -------------------------------------------------------------------------
    credits_packs_page.fill_in_zip_code_field(
        CreditPackType.EXPLORER.value, '35208')
    assert_proceed_button_is_enabled(
        errors, CreditPackType.EXPLORER.value,
        help_text=FILL_BACK_MESSAGE.format(ZIP))

    # -------------------------------------------------------------------------
    # 10. Street Address cannot contain invalid symbols
    # -------------------------------------------------------------------------
    invalid_street = '_'
    credits_packs_page.fill_in_street_address_field(
        CreditPackType.EXPLORER.value, invalid_street)
    validate_field(
        errors_list=errors, pack_name=CreditPackType.EXPLORER.value,
        value=invalid_street,
        validation_message_selector=ValidationMessageSelectors.
            STREET_INVALID_SYMBOLS.value, field_name=STREET_ADDRESS,
        field_element=credits_packs_page.explorer_street_address_field,
        help_text=ENTER_INTO_FIELD.format(invalid_street, STREET_ADDRESS)
    )
    credits_packs_page.fill_in_street_address_field(
        CreditPackType.EXPLORER.value, valid_street)

    # -------------------------------------------------------------------------
    # 11. City cannot contain invalid symbols
    # -------------------------------------------------------------------------
    invalid_city = '='
    credits_packs_page.fill_in_city_field(
        CreditPackType.EXPLORER.value, invalid_city)
    validate_field(
        errors_list=errors, pack_name=CreditPackType.EXPLORER.value,
        value=invalid_city,
        validation_message_selector=ValidationMessageSelectors.
            CITY_INVALID_SYMBOLS.value, field_name=CITY,
        field_element=credits_packs_page.explorer_city_field,
        help_text=ENTER_INTO_FIELD.format(invalid_city, CITY)
    )
    credits_packs_page.fill_in_city_field(
        CreditPackType.EXPLORER.value, valid_city)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def validate_field(credits_packs_page, assert_element_is_present,
                   assert_proceed_button_is_disabled):
    """
    Validates Credit Pack shipping info field:
    1. Asserts validation message after entering wrong value
    2. Asserts field is highlighted
    3. Asserts Proceed button is disabled
    """
    def validate_field(
            errors_list, pack_name, value, validation_message_selector,
            field_name, field_element, help_text=''):

        assert_element_is_present(
            credits_packs_page, validation_message_selector, errors_list,
            VALIDATION_ERROR_MESSAGE.format(value, field_name)
        )
        credits_packs_page.click_selector(validation_message_selector)
        class_value = credits_packs_page.get_element_attribute_value(
            field_element, HtmlAttribute.CLASS.value
        )
        if class_value != VALIDATED_CLASS:
            errors_list.append(HIGHLIGHT_ERROR.format(
                field_name, value, VALIDATED_CLASS, class_value)
            )
        assert_proceed_button_is_disabled(errors_list, pack_name, help_text)

    return validate_field


@fixture
def validate_cleared_field(credits_packs_page, assert_element_is_present,
                           assert_proceed_button_is_disabled):
    """
    Validates Credit Pack shipping info field which was cleared:
    1. Asserts validation message after clearing the field
    2. Asserts field is highlighted
    3. Asserts Proceed button is disabled
    """
    def validate_field(
            errors_list, pack_name, validation_message_selector, field_name,
            field_element, help_text=''):

        assert_element_is_present(
            credits_packs_page, validation_message_selector, errors_list,
            VALIDATION_CLEAR_ERROR_MESSAGE.format(field_name)
        )
        class_value = credits_packs_page.get_element_attribute_value(
            field_element, HtmlAttribute.CLASS.value
        )
        if class_value != VALIDATED_CLASS:
            errors_list.append(HIGHLIGHT_CLEAR_ERROR.format(
                field_name, VALIDATED_CLASS, class_value)
            )
        assert_proceed_button_is_disabled(errors_list, pack_name, help_text)

    return validate_field


@fixture
def assert_proceed_button_is_disabled(credits_packs_page):
    """Asserts <Proceed> button is disabled."""

    def proceed_button_is_disabled(errors_list, pack_name, help_text):

        if credits_packs_page.is_proceed_button_enabled(pack_name):
            errors_list.append(
                f'<Proceed> button must be disabled after {help_text}')

    return proceed_button_is_disabled


@fixture
def assert_proceed_button_is_enabled(credits_packs_page):
    """Asserts <Proceed> button is enabled."""

    def proceed_button_is_enabled(errors_list, pack_name, help_text):

        if not credits_packs_page.is_proceed_button_enabled(pack_name):
            errors_list.append(
                f'<Proceed> button must be enabled after {help_text}')

    return proceed_button_is_enabled


ZIP = 'Zip Code'
STATE_ADDRESS = 'State Address'
STREET_ADDRESS = 'Street Address'
CITY = 'City'
VALIDATED_CLASS = 'dr-form-field-control-validated'
VALIDATION_ERROR_MESSAGE = \
    'Missing/wrong validation message after entering {} into {} field'
VALIDATION_CLEAR_ERROR_MESSAGE = \
    'Missing/wrong validation message after clearing {} field'
ENTER_INTO_FIELD = 'entering {} into {} field'
CLEAR_FIELD = 'clearing {} field'
HIGHLIGHT_ERROR = '{} field is not highlighted after entering "{}". ' \
                  'Class attribute value must be {}, got "{}".'
HIGHLIGHT_CLEAR_ERROR = '{} field is not highlighted after clearing it. ' \
                        'Class attribute value must be {}, got "{}".'
FILL_BACK_MESSAGE = 'clearing and then filling in {} again'


class ValidationMessageSelectors(Enum):
    ZIP_CODE = TEXT.format('Zip Code cannot contain invalid symbols')
    STATE_ADDRESS = TEXT.format('State can include alphabets only')
    REQUIRED_FIELDS = TEXT.format('Please fill in all the required fields')
    STREET_INVALID_SYMBOLS = TEXT.format(
        'Street Address cannot contain invalid symbols')
    CITY_INVALID_SYMBOLS = TEXT.format('City cannot contain invalid symbols')
    STATE_2_LETTERS = TEXT.format('State can include 2 letters')
