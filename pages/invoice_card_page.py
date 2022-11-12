from re import findall

from pages.base_page import BasePage
from utils.selectors_enums import InvoiceCardPageSelectors
from utils.constants import ASSERT_ERRORS
from utils.errors import ElementIsAbsentException


class InvoiceCardPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def view_invoice_details_button(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.VIEW_INVOICE_DETAILS_BUTTON.value)

    @property
    def close_invoice_details_from_card_button(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.CLOSE_INVOICE_DETAILS_FROM_CARD_BUTTON.value)

    @property
    def close_invoice_details_x_button(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.CLOSE_INVOICE_DETAILS_X_BUTTON.value)

    @property
    def invoice_details_contact_dr_button(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.INVOICE_DETAILS_CONTACT_DR_BUTTON.value)

    @property
    def download_invoice_icon(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.CARD_INVOICE_DOWNLOAD_ICON.value)

    @property
    def download_paid_invoice_button(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.DOWNLOAD_PAID_INVOICE_BUTTON.value)

    @property
    def download_receipt_button(self):
        return self.wait_for_element(
            InvoiceCardPageSelectors.DOWNLOAD_RECEIPT_BUTTON.value)

    def view_invoice_details(self):
        """
        Clicks View Invoice Details button at Invoice card
        which opens Invoice Details at the right side of the page.
        """
        self.click_element(self.view_invoice_details_button)
        self.wait_for_element(
            InvoiceCardPageSelectors.INVOICE_DETAILS_CONTENT.value
        )
        self.logger.info('Opened Invoice Details')

    def close_invoice_details(self, close_from_card=True):
        """
        Closes Invoice Details (at the right of the page) by either clicking 'Close invoice details X' button
        or Close X button in top right corner of invoice Details.
        Raises ElementIsAbsentException if 'View invoice details' button is not present after closing Invoice Details.
        """
        if close_from_card:
            self.click_element(self.close_invoice_details_from_card_button)
        else:
            self.click_element(self.close_invoice_details_x_button)

        if not self.is_element_present(
                InvoiceCardPageSelectors.VIEW_INVOICE_DETAILS_BUTTON.value
        ):
            raise ElementIsAbsentException(
                InvoiceCardPageSelectors.VIEW_INVOICE_DETAILS_BUTTON.value,
                'Invoice Details was not closed.'
            )
        self.logger.info('Closed Invoice Details')

    def get_invoice_number_from_invoice_details(self):
        """
        Returns invoice number (e.g. C7B07423-0004)
        retrieved from invoice details header, e.g.INVOICE #C7B07423-0004
        """
        invoice_details_content = self.get_inner_text(
            InvoiceCardPageSelectors.INVOICE_DETAILS_CONTENT.value
        )
        invoice_number = self._get_invoice_number(invoice_details_content)
        self.logger.info(
            'Invoice number: %s', invoice_number
        )
        return invoice_number

    def get_receipt_number_from_file_name(self, file_name):
        """
        Returns receipt number (e.g. 2301-0660) from downloaded receipt file name,
        e.g. Receipt-2481-5191.pdf
        """
        receipt_number = self._get_receipt_number(file_name)
        self.logger.info(
            'Receipt number: %s', receipt_number
        )
        return receipt_number

    def check_contact_dr_from_invoice_details(self):
        """
        Clicks Contact DataRobot button at the bottom of invoice details.
        Asserts email and phone at popover which appears after the button is clicked.
        """
        self.click_element(self.invoice_details_contact_dr_button)

        message = 'Wrong {} at invoice details Contact DataRobot popover'
        errors = []

        if not self.is_element_present(
                InvoiceCardPageSelectors.
                        INVOICE_DETAILS_CONTACT_DR_POPOVER_EMAIL.value):
            errors.append(message.format('email'))

        if not self.is_element_present(
                InvoiceCardPageSelectors.
                        INVOICE_DETAILS_CONTACT_DR_POPOVER_PHONE.value):
            errors.append(message.format('phone'))

        assert not errors, ASSERT_ERRORS.format('\n'.join(errors))

        self.logger.info(
            'Validated invoice details at Contact DataRobot popover')

    def download_invoice(self, paid_invoice=False):
        """
        Downloads unpaid invoice by clicking Download invoice icon
        at top right corner of invoice card if paid_invoice=False,
        otherwise downloads paid invoice by clicking 'Download invoice' button.
        Returns invoice file name.
        """
        if paid_invoice:
            invoice_file = self.download_file(self.download_paid_invoice_button)
        else:
            invoice_file = self.download_file(self.download_invoice_icon)

        self.logger.info(
            'Downloaded invoice: %s', invoice_file
        )
        return invoice_file

    def download_receipt(self):
        """
        Downloads receipt by clicking 'Download receipt' button.
        Returns receipt file name.
        """
        receipt_file = self.download_file(self.download_receipt_button)

        self.logger.info(
            'Downloaded receipt: %s', receipt_file
        )
        return receipt_file

    def buy_pack(self, price):
        """
        Clicks 'Pay {price}' button to buy a credit pack.
        {price} is either $99.99 (Explorer) or $499.99 (Accelerator).
        Waits for 'Invoice paid' text to confirm the pack has been bought.
        """
        pay_button = InvoiceCardPageSelectors.PAY_PRICE_BUTTON.value.format(
            price
        )
        self.wait_for_element(pay_button)
        self.click_selector(pay_button)

        self.wait_for_element(
            InvoiceCardPageSelectors.INVOICE_PAID_TEXT.value
        )
        self.logger.info('Paid %s for credit pack', price)

    @staticmethod
    def _get_invoice_number(content):
        """Retrieves invoice number (e.g. 3A89AB70-0001) from passed string."""

        return findall('[a-zA-Z0-9]{8}-[0-9]{4}', content)[0]

    @staticmethod
    def _get_receipt_number(content):
        """Retrieves receipt number (e.g. 2301-0660) from passed string."""

        return findall('[0-9]{4}-[0-9]{4}', content)[0]
