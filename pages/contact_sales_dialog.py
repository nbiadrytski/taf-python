from pages.base_page import BasePage
from utils.selectors_enums import (
    ContactSalesDialogSelectors,
    HomePageSelectors,
    TEXT
)
from utils.errors import ElementAttributeTimeoutException


CONTACT_SALES_DIALOG = 'Contact Sales dialog'


class ContactSalesDialog(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def close_x_button(self):
        return self.wait_for_element(
            ContactSalesDialogSelectors.CLOSE_X_BUTTON.value)

    @property
    def text_field(self):
        return self.wait_for_element(
            ContactSalesDialogSelectors.TEXT_AREA.value)

    @property
    def category_dropdown(self):
        return self.wait_for_element(
            ContactSalesDialogSelectors.CATEGORY_DROPDOWN.value)

    @property
    def send_button(self):
        return self.wait_for_element(
            ContactSalesDialogSelectors.SEND_BUTTON.value)

    def close_dialog(self):
        """Closes Contact Sales dialog."""

        self.click_element(self.close_x_button)
        self.is_element_present(
            HomePageSelectors.BUY_CREDITS.value, raise_error=True,
            help_text=f'Did not close {CONTACT_SALES_DIALOG}'
        )
        self.logger.info('Closed %s.', CONTACT_SALES_DIALOG)

    def fill_in_text_field(self, text):
        """Enters text into 'What's on your mind?' text field."""

        text_field = '"What\'s on your mind?" field'
        self.enter_text(self.text_field, text)
        text_content = self.get_element_text_content(self.text_field)

        if text_content != text:
            raise ValueError(
                f'{CONTACT_SALES_DIALOG} {text_field} must contain "{text}"'
                f', but contains "{text_content}"'
            )
        self.logger.info(
            'Entered %s into %s of %s', text, text_field, CONTACT_SALES_DIALOG)

    def expand_category_dropdown(self):
        """Expands Contact Sales dialog Category dropdown."""

        self.click_element(self.category_dropdown)

        attr = 'aria-expanded'
        is_dropdown_expanded = self.get_element_attribute_value(
            self.category_dropdown, attr)

        if is_dropdown_expanded != 'true':
            raise ElementAttributeTimeoutException(
                attr, ContactSalesDialogSelectors.CATEGORY_DROPDOWN.value,
                f'{CONTACT_SALES_DIALOG} Category dropdown is not expanded'
            )
        self.logger.info('Expanded %s category dropdown', CONTACT_SALES_DIALOG)

    def select_category(self, category):
        """
        Selects a category from Contact Sales Category dropdown.
        See utils.data_enums.ContactSalesCategory for categories list.
        """
        self.wait_for_element(TEXT.format(category))
        self.click_selector(TEXT.format(category))
        self.is_element_present(
            ContactSalesDialogSelectors.
                SELECTED_CATEGORY.value.format(category), raise_error=True, 
            help_text=f'{CONTACT_SALES_DIALOG} {category} category was not selected'
        )
        self.logger.info('Selected %s category from %s Category dropdown', 
                         category, CONTACT_SALES_DIALOG)

    def send_message(self):
        """
        Click Contact Sales dialog 'Send' button to send a message.
        Waits for 'Your message has been sent' notification to confirm the sending was successful.
        """
        self.click_element(self.send_button)
        self.wait_for_element(
            ContactSalesDialogSelectors.MESSAGE_SENT_TEXT.value,
            help_text=f'{CONTACT_SALES_DIALOG} message was not sent'
        )
        self.logger.info('%s message was sent', CONTACT_SALES_DIALOG)
