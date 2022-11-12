from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import ASSERT_ERRORS
from utils.selectors_enums import (
    CreditsPacksPageSelectors,
    ContactSalesDialogSelectors,
    TEXT,
    TEST_ID
)
from utils.data_enums import (
    HtmlAttribute,
    ContactSalesCategory,
    Envs
)
from pages.contact_sales_dialog import CONTACT_SALES_DIALOG


@mark.ui
def test_buy_credits_modal_content(setup_and_sign_in_payg_user,
                                   home_page, env_params,
                                   credits_packs_page,
                                   assert_cards_titles,
                                   validate_contact_sales_card,
                                   validate_explorer_card,
                                   validate_accelerator_card,
                                   validate_page_header_content,
                                   validate_page_footer_content,
                                   contact_sales_dialog,
                                   validate_contact_sales_dialog):

    setup_and_sign_in_payg_user()
    # Assertion errors will be appended to this list
    errors = []

    home_page.go_to_credits_packs_modal()
    # --------------------------------------------------------
    # 1. Assert Explorer, Accelerator, Contact Sales card titles
    # --------------------------------------------------------
    assert_cards_titles(errors)

    # --------------------------------------------------------
    # 2. Validate Contact Sales card
    # --------------------------------------------------------
    validate_contact_sales_card(errors)

    # --------------------------------------------------------
    # 3. Validate Explorer pack card
    # --------------------------------------------------------
    validate_explorer_card(errors)

    # --------------------------------------------------------
    # 4. Validate Accelerator pack card
    # --------------------------------------------------------
    validate_accelerator_card(errors)

    # --------------------------------------------------------
    # 5. Validate page header content
    # --------------------------------------------------------
    validate_page_header_content(errors)

    # --------------------------------------------------------
    # 6. Validate page footer content
    # --------------------------------------------------------
    validate_page_footer_content(errors)

    # --------------------------------------------------------
    # 7. User can open and close Contact Sales dialog
    # --------------------------------------------------------
    credits_packs_page.open_contact_sales()
    contact_sales_dialog.close_dialog()

    # --------------------------------------------------------
    # 8. Validate Contact Sales dialog content
    # --------------------------------------------------------
    home_page.go_to_credits_packs_modal()
    credits_packs_page.open_contact_sales()
    validate_contact_sales_dialog(errors)

    # --------------------------------------------------------
    # 9. Send a message from Contact Sales dialog
    # --------------------------------------------------------
    if Envs.PROD.value in env_params[0]:
        contact_sales_dialog.send_message()

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def get_pack_cards_elements(credits_packs_page):
    """Returns ElementHandle elements of Explorer and Accelerator cards."""

    def cards_elements():

        explorer_card_element, accel_card_element, _\
            = credits_packs_page.get_child_elements_by_selector(
            CreditsPacksPageSelectors.PACKS_CONTENT.value
        )
        return explorer_card_element, accel_card_element

    return cards_elements


@fixture
def get_pack_cards_front_side_elements(credits_packs_page, get_pack_cards_elements):
    """Returns front side ElementHandle element of Explorer and Accelerator card elements."""

    def pack_cards_front_side_elements():

        explorer_card_element, accel_card_element = get_pack_cards_elements()
        _, explorer_front_side = credits_packs_page.get_child_elements(
            explorer_card_element
        )
        _, accel_front_side = credits_packs_page.get_child_elements(
            accel_card_element
        )
        return explorer_front_side, accel_card_element

    return pack_cards_front_side_elements


@fixture
def assert_cards_titles(credits_packs_page, get_pack_cards_front_side_elements,
                        assert_element_is_present):
    """Asserts titles of Explorer, Accelerator and Contact Sales cards."""

    def cards_titles(errors_list):

        explorer_front_side, accel_card_element = get_pack_cards_front_side_elements()
        explorer_text = credits_packs_page.get_element_inner_text(explorer_front_side)
        accel_text = credits_packs_page.get_element_inner_text(accel_card_element)

        error_message = 'Expected {} title {} not found in card content: "{}"'
        explorer_title = 'EXPLORER PACK'
        if explorer_title not in explorer_text:
            errors_list.append(
                error_message.format(EXPLORER_CARD, explorer_title, explorer_text))

        accel_title = 'ACCELERATOR PACK'
        if accel_title not in accel_text:
            errors_list.append(
                error_message.format(ACCEL_CARD, accel_title, accel_text))

        if not credits_packs_page.is_element_present(
                ContactSalesCardSelectors.TITLE.value):
            errors_list.append('Wrong Contact Sales card title.')

    return cards_titles


@fixture
def assert_card_image(credits_packs_page, assert_attribute_value_contains):
    """Asserts image is present at card"""

    def card_image(errors_list, image_selector, help_text=''):

        assert_attribute_value_contains(
            credits_packs_page, image_selector, HtmlAttribute.SRC.value,
            expected_value='data:image/svg+xml;base64,',
            errors_list=errors_list, help_text=help_text)

    return card_image


@fixture
def assert_contact_sales_card_content(credits_packs_page,
                                      assert_element_is_present):
    """Asserts Contact Us card content."""

    def contact_sales_card_content(errors_list, content_list):

        for line in content_list:
            assert_element_is_present(credits_packs_page, line, errors_list,
                                      'Check Contact Sales card content')

    return contact_sales_card_content


@fixture
def validate_contact_sales_card(assert_card_image, assert_contact_sales_card_content):
    """Validates image and text content of Contact Sales card."""

    def contact_sales_card(errors_list):

        assert_card_image(
            errors_list, ContactSalesCardSelectors.IMAGE.value,
            CHECK_IMAGE_MESSAGE.format(CONTACT_SALES_CARD)
        )
        assert_contact_sales_card_content(errors_list, CONTACT_SALES_CARD_CONTENT)

    return contact_sales_card


@fixture
def validate_explorer_card(
        credits_packs_page, assert_card_image, get_pack_cards_front_side_elements):
    """Validates image and text content of Explorer card."""

    def explorer_card(errors_list):

        assert_card_image(
            errors_list, CreditsPacksPageSelectors.EXPLORER_CARD_IMAGE.value,
            CHECK_IMAGE_MESSAGE.format(EXPLORER_CARD)
        )
        explorer_front_side, _ = get_pack_cards_front_side_elements()
        explorer_text = credits_packs_page.get_element_inner_text(explorer_front_side)

        if EXPLORER_CONTENT != explorer_text:
            errors_list.append(
                CARD_CONTENT_ERROR_MESSAGE.format(
                    EXPLORER_CARD, EXPLORER_CONTENT, explorer_text))

    return explorer_card


@fixture
def validate_accelerator_card(
        credits_packs_page, assert_card_image, get_pack_cards_front_side_elements):
    """Validates image and text content of Accelerator card."""

    def accelerator_card(errors_list):

        assert_card_image(
            errors_list, CreditsPacksPageSelectors.ACCEL_CARD_IMAGE.value,
            CHECK_IMAGE_MESSAGE.format(ACCEL_CARD)
        )
        _, accel_front_side = get_pack_cards_front_side_elements()
        accel_text = credits_packs_page.get_element_inner_text(accel_front_side)

        if ACCEL_CONTENT not in accel_text:
            errors_list.append(
                CARD_CONTENT_ERROR_MESSAGE.format(ACCEL_CARD, ACCEL_CONTENT, accel_text))

    return accelerator_card


@fixture
def validate_page_header_content(credits_packs_page, assert_element_is_present):
    """Validates image and text content of Buy Credits modal header."""

    def page_header_content(errors_list):

        dr_image = credits_packs_page.get_attribute_value(
            PageHeaderSelectors.DR_LOGO.value, HtmlAttribute.SRC.value, raise_error=False
        )
        expected_image = '/static/assets/logo-dark.svg'
        if dr_image != expected_image:
            errors_list.append(
                f'Expected DR logo at page header: {expected_image}, got: {dr_image}'
            )
        assert_element_is_present(
            credits_packs_page, PageHeaderSelectors.TEXT_CONTENT.value, errors_list,
            'Wrong/missing text content at page header')

    return page_header_content


@fixture
def validate_page_footer_content(credits_packs_page, assert_element_is_present):
    """Validates link and text content of Buy Credits modal footer."""

    def page_footer_content(errors_list):

        for line in PAGE_FOOTER_CONTENT:
            assert_element_is_present(
                credits_packs_page, line, errors_list, 'Check content of page footer'
            )
        credit_allocations_link = credits_packs_page.get_attribute_value(
            PageFooterSelectors.CREDIT_ALLOCATIONS_LINK.value, HtmlAttribute.HREF.value,
            raise_error=False
        )
        if credit_allocations_link != CREDIT_ALLOCATIONS_LINK:
            errors_list.append(
                f'Expected Credit allocation details link: {CREDIT_ALLOCATIONS_LINK},'
                f' got: {credit_allocations_link}')

    return page_footer_content


@fixture
def validate_contact_sales_dialog(contact_sales_dialog, assert_element_is_present):
    """
    Validates Contact Sales dialog content:
    1. Asserts dialog Title
    2. Asserts Pricing Info category is selected by default
    3. Expands Category dropdown
    4. Selects Request More Credits category and asserts it's selected
    5. Enters text into text area and asserts it's entered
    5. Asserts "Choose file" button for screenshots upload is present
    """
    def validate_contact_sales(errors_list):

        assert_element_is_present(
            contact_sales_dialog, ContactSalesDialogSelectors.CONTACT_US_TITLE.value,
            errors_list, f'{CONTACT_SALES_DIALOG} Title is wrong.'
        )
        assert_element_is_present(
            contact_sales_dialog,
            ContactSalesDialogSelectors.SELECTED_CATEGORY.value.format(
                ContactSalesCategory.PRICING_INFO.value), errors_list,
            f'{CONTACT_SALES_DIALOG} {ContactSalesCategory.PRICING_INFO.value}'
            f' category must be selected by default'
        )
        contact_sales_dialog.expand_category_dropdown()
        contact_sales_dialog.select_category(ContactSalesCategory.MORE_CREDITS.value)
        contact_sales_dialog.fill_in_text_field('E2E Self Service UI Test: ignore me')
        assert_element_is_present(
            contact_sales_dialog,
            ContactSalesDialogSelectors.CHOOSE_FILE_FOR_UPLOAD_BUTTON.value,
            errors_list, f'{CONTACT_SALES_DIALOG} "Choose file" button is absent.')

    return validate_contact_sales


class ContactSalesCardSelectors(Enum):
    CARD_CONTENT = f'{CreditsPacksPageSelectors.PACKS_CONTENT.value} div.card-container div.card-content'
    TITLE = f'{CARD_CONTENT} span.section-header >> text=Enterprise plans'
    IMAGE = f'{CARD_CONTENT} img.card-icon'
    CALL_BOLD_TEXT = f'{CARD_CONTENT} span.page-header >> text=Call'
    UNLIMITED_USAGE_TEXT = f'{CARD_CONTENT} span.section-header >> text=Unlimited Usage'
    TEXT_LINES_LIST = f'{CARD_CONTENT} ul li.checked >> text='
    TEXT_LINE1 = f'{TEXT_LINES_LIST}Unlimited AI Platform Usage'
    TEXT_LINE2 = f'{TEXT_LINES_LIST}DataRobot Time Series'
    TEXT_LINE3 = f'{TEXT_LINES_LIST}Model Compliance & Portability'
    TEXT_LINE4 = f'{TEXT_LINES_LIST}Full Blueprint Documentation'
    TEXT_LINE5 = f'{TEXT_LINES_LIST}Access to Beta Features'
    TEXT_LINE6 = f'{TEXT_LINES_LIST}On Premise Options'
    TEXT_LINE7 = f'{TEXT_LINES_LIST}Premium Support ***'


class PageHeaderSelectors(Enum):
    DR_LOGO = 'div.logo-title img.logo'
    TEXT_CONTENT = TEXT.format('10x your productivity with the DataRobot AI Platform')


class PageFooterSelectors(Enum):
    FOOTER_ELEMENT = 'div.notes ul li span.sub-text >> text='
    TEXT_LINE1 = f'{FOOTER_ELEMENT}Purchasing credits will transfer you to Stripe, ' \
                 f'our secure third party payment card processor. ' \
                 f'DataRobot will not have access to your billing information.'
    TEXT_LINE2 = f'{FOOTER_ELEMENT}* Credits are expended when you use the AI Platform for ' \
                 f'modeling, predictions, data processing, and deployments. '
    TEXT_LINE3 = f'{FOOTER_ELEMENT}** You can access DataRobot Data Prep capabilities ' \
                 f'as long as you have at least 1 credit on your account.'
    TEXT_LINE4 = f'{FOOTER_ELEMENT}*** Premium support includes priority email technical support ' \
                 f'including q&a with our Customer Facing Data Scientists.'
    CREDIT_ALLOCATIONS_LINK = TEST_ID.format('credit-learn-more')


CONTACT_SALES_CARD_CONTENT = [
    ContactSalesCardSelectors.TEXT_LINE1.value,
    ContactSalesCardSelectors.TEXT_LINE2.value,
    ContactSalesCardSelectors.TEXT_LINE3.value,
    ContactSalesCardSelectors.TEXT_LINE4.value,
    ContactSalesCardSelectors.TEXT_LINE5.value,
    ContactSalesCardSelectors.TEXT_LINE6.value,
    ContactSalesCardSelectors.TEXT_LINE7.value,
]

PAGE_FOOTER_CONTENT = [
    PageFooterSelectors.TEXT_LINE1.value,
    PageFooterSelectors.TEXT_LINE2.value,
    PageFooterSelectors.TEXT_LINE3.value,
    PageFooterSelectors.TEXT_LINE4.value,
]

EXPLORER_CARD = 'Explorer card'
ACCEL_CARD = 'Accelerator card'
CONTACT_SALES_CARD = 'Contact Sales card'
CHECK_IMAGE_MESSAGE = 'Check {} image'
CARD_CONTENT_ERROR_MESSAGE = 'Expected {} content: {}, but got: {}'
CREDIT_ALLOCATIONS_LINK = 'https://community.datarobot.com/t5/draft-discussions/billing-help-and-faqs/m-p/8329'

EXPLORER_CONTENT = 'CREDIT PACK\n' \
                   'EXPLORER PACK\n\n' \
                   '$\n99\n\n' \
                   '4,000 AI PLATFORM CREDITS*\n' \
                   'Best for smaller datasets and limited prediction requirements\n' \
                   'Buy Now\n' \
                   'Includes access to AutoML and Visual AI learning, deployments, and MLOps monitoring.' \
                   ' Credit packs also include unlimited Data Prep access** and Community support.'

ACCEL_CONTENT = 'CREDIT PACK\n' \
                'ACCELERATOR PACK\n\n' \
                '$\n499\n\n' \
                '20,000 AI PLATFORM CREDITS*\n' \
                'Best for larger datasets and multiple deployed models\n' \
                'Buy Now\n' \
                'Includes access to AutoML and Visual AI learning, deployments, and MLOps monitoring.' \
                ' Credit packs also include unlimited Data Prep access** and Community support.'
