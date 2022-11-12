from pages.base_page import BasePage
from pages.invoice_card_page import InvoiceCardPage
from utils.selectors_enums import CreditsPacksPageSelectors
from utils.data_enums import (
    Envs,
    CreditPackType
)


class CreditsPacksPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def buy_explorer_pack_button(self):
        return self.wait_for_element(
            CreditsPacksPageSelectors.BUY_EXPLORER_PACK_BUTTON.value)

    @property
    def buy_accel_pack_button(self):
        return self.wait_for_element(
            CreditsPacksPageSelectors.BUY_ACCEL_PACK_BUTTON.value)

    @property
    def explorer_street_address_field(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.EXPLORER_STREET_ADDRESS_FIELD_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.EXPLORER_STREET_ADDRESS_FIELD_PROD.value)

    @property
    def accel_street_address_field(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.ACCEL_STREET_ADDRESS_FIELD_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.ACCEL_STREET_ADDRESS_FIELD_PROD.value)

    @property
    def explorer_city_field(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.EXPLORER_CITY_FIELD_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.EXPLORER_CITY_FIELD_PROD.value)

    @property
    def accel_city_field(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.ACCEL_CITY_FIELD_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.ACCEL_CITY_FIELD_PROD.value)

    @property
    def explorer_state_dropdown(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.EXPLORER_STATE_DROPDOWN_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.EXPLORER_STATE_ADDRESS_FIELD_PROD.value)

    @property
    def accel_state_dropdown(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.ACCEL_STATE_DROPDOWN_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.ACCEL_STATE_ADDRESS_FIELD_PROD.value)

    @property
    def explorer_zip_field(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.EXPLORER_ZIP_FIELD_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.EXPLORER_ZIP_FIELD_PROD.value)

    @property
    def accel_zip_field(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.ACCEL_ZIP_FIELD_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.ACCEL_ZIP_FIELD_PROD.value)

    @property
    def explorer_country_dropdown(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.EXPLORER_COUNTRY_DROPDOWN_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.EXPLORER_COUNTRY_DROPDOWN_PROD.value)

    @property
    def accel_country_dropdown(self):
        if Envs.STAGING.value in self.app_host:
            return self.wait_for_element(
                CreditsPacksPageSelectors.ACCEL_COUNTRY_DROPDOWN_STAGING.value
            )
        return self.wait_for_element(
            CreditsPacksPageSelectors.ACCEL_COUNTRY_DROPDOWN_PROD.value)

    @property
    def proceed_button(self):
        return self.wait_for_element(
            CreditsPacksPageSelectors.PROCEED_BUTTON.value)

    @property
    def contact_sales_button(self):
        return self.wait_for_element(
            CreditsPacksPageSelectors.CONTACT_SALES_BUTTON.value)

    def open_credit_pack_shipping_info(self, pack_name):
        """
        Flips Credit Pack card to the side with ENTER YOUR SHIPPING INFORMATION text by clicking Buy Now button.
        'pack_name' param is the value of CreditPackType enum, e.g. EXPLORER_PACK, ACCELERATOR_PACK.
        Confirms the card is flipped by checking that element
        with class 'card-container card-border flip-content' is present.
        """
        if pack_name == CreditPackType.EXPLORER.value:
            self.click_element(self.buy_explorer_pack_button)
        else:
            self.click_element(self.buy_accel_pack_button)

        self.is_element_present(
            CreditsPacksPageSelectors.PACK_CARD_BACK_SIDE.value, raise_error=True
        )
        self.logger.info('Flipped %s card to the shipping info side', pack_name)

    def fill_in_shipping_info(self, pack_name,
                              street_address='4139 Petunia Way',
                              city='Birmingham', zip_code='35208'):
        """
        Fills in Credit Pack shipping info:
        1. Checks if Proceed button is disabled
        2. Fills in Street Address field
        3. Fills in City field
        4. Checks if default State is Alabama
        5. Fills in Zip code field
        6. Checks if default selected country is US
        7. Checks if Proceed button is enabled
        """
        if self.is_proceed_button_enabled(pack_name):
            raise ValueError(
                f'{pack_name} Proceed button must disabled with just flipped card')

        self.fill_in_street_address_field(pack_name, street_address)
        self.fill_in_city_field(pack_name, city)
        if not self.is_alabama_default_state(pack_name):
            raise ValueError(
                f'{pack_name} card default state is not Alabama'
            )
        if not self.is_us_default_country(pack_name):
            raise ValueError(f'{pack_name} card default country is not US')
        self.fill_in_zip_code_field(pack_name, zip_code)

        if not self.is_us_default_country(pack_name):
            raise ValueError(f'{pack_name} card default country is not US')

        if not self.is_proceed_button_enabled(pack_name):
            raise ValueError(f'{pack_name} Proceed button must enabled with '
                             f'shipping info filled in.')

    def fill_in_street_address_field(self, pack_name, street_address,
                                     check_text_is_entered=True):
        """
        Enters text into Credit Pack card Street Address field.
        Optionally, checks if text was indeed entered.
        """
        log_message = 'Entered "%s" into %s street address field'
        if pack_name == CreditPackType.EXPLORER.value:
            self.enter_text(
                self.explorer_street_address_field, street_address
            )
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.explorer_street_address_field, street_address
                )
            self.logger.info(log_message, street_address, pack_name)
        else:
            self.enter_text(
                self.accel_street_address_field, street_address
            )
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.accel_street_address_field, street_address
                )
            self.logger.info(log_message, street_address, pack_name)

    def fill_in_city_field(self, pack_name, city,
                           check_text_is_entered=True):
        """
        Enters text into Credit Pack card City field.
        Optionally, checks if text was indeed entered.
        """
        log_message = 'Entered "%s" into %s city field'
        if pack_name == CreditPackType.EXPLORER.value:
            self.enter_text(self.explorer_city_field, city)
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.explorer_city_field, city
                )
            self.logger.info(log_message, city, pack_name)
        else:
            self.enter_text(self.accel_city_field, city)
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.accel_city_field, city
                )
            self.logger.info(log_message, city, pack_name)

    def fill_in_state_address_field(self, pack_name, state_address,
                                    check_text_is_entered=True):
        """
        Enters text into Credit Pack card State Address field.
        Optionally, checks if text was indeed entered.
        """
        log_message = 'Entered "%s" into %s State Address field'
        if pack_name == CreditPackType.EXPLORER.value:
            self.enter_text(
                self.explorer_state_dropdown, state_address)
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.explorer_state_dropdown, state_address
                )
            self.logger.info(log_message, state_address, pack_name)
        else:
            self.enter_text(
                self.accel_state_dropdown, state_address)
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.accel_state_dropdown, state_address
                )
            self.logger.info(log_message, state_address, pack_name)

    def fill_in_zip_code_field(self, pack_name, zip_code,
                               check_text_is_entered=True):
        """
        Enters text into Credit Pack card Zip code field.
        Optionally, checks if text was indeed entered.
        """
        log_message = 'Entered "%s" into %s Zip Code field'
        if pack_name == CreditPackType.EXPLORER.value:
            self.enter_text(self.explorer_zip_field, zip_code)
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.explorer_zip_field, zip_code
                )
            self.logger.info(log_message, zip_code, pack_name)
        else:
            self.enter_text(self.accel_zip_field, zip_code)
            if check_text_is_entered:
                self.confirm_text_is_entered_into_element(
                    self.accel_zip_field, zip_code
                )
            self.logger.info(log_message, zip_code, pack_name)

    def is_us_default_country(self, pack_name):
        """Asserts pack_name default country is United States, otherwise raises ValueError"""

        expected_country = 'United States'
        error_log_message = '%s card default country is "%s", expected: "%s"'
        debug_log_message = '%s card default country is "%s"'

        if pack_name == CreditPackType.EXPLORER.value:
            country = self.get_element_inner_text(self.explorer_country_dropdown)
            if country != expected_country:
                self.logger.error(
                    error_log_message, pack_name, country, expected_country)
                return False

            self.logger.debug(debug_log_message, pack_name, country)
            return True
        else:
            country = self.get_element_inner_text(self.accel_country_dropdown)

            if country != expected_country:
                self.logger.error(error_log_message, pack_name, country, expected_country)
                return False

            self.logger.debug(debug_log_message, pack_name, country)
            return True

    def is_alabama_default_state(self, pack_name):
        """
        Asserts pack_name default State is Alabama,
        otherwise raises ValueError
        """
        expected_state = 'Alabama'
        error_log_message = '%s card default state is "%s", expected: "%s"'
        debug_log_message = '%s card default state is "%s"'

        if pack_name == CreditPackType.EXPLORER.value:
            state = self.get_element_inner_text(self.explorer_state_dropdown)
            if state != expected_state:
                self.logger.error(
                    error_log_message, pack_name, state, expected_state)
                return False

            self.logger.debug(debug_log_message, pack_name, state)
            return True
        else:
            state = self.get_element_inner_text(self.accel_state_dropdown)

            if state != expected_state:
                self.logger.error(
                    error_log_message, pack_name, state, expected_state)
                return False

            self.logger.debug(debug_log_message, pack_name, state)
            return True

    def is_proceed_button_enabled(self, pack_name):
        """Returns True if Credit Pack card Proceed button is enabled, otherwise returns False"""

        if self.does_element_have_disabled_attribute(self.proceed_button):
            self.logger.info('%s card Proceed button is disabled', pack_name)
            return False

        self.logger.info('%s card Proceed button is enabled', pack_name)
        return True

    def proceed_to_invoice(self):
        """
        Clicks Proceed button from Credit Pack card which opens Stripe invoice tab.
        Checks if new page title is Stripe Invoice.
        Returns new invoice_page object of InvoiceCardPage type.
        """
        invoice_page = self.open_new_tab(self.proceed_button, InvoiceCardPage)
        actual_title = invoice_page.page_title
        expected_title = 'Stripe Invoice'

        if expected_title not in actual_title:
            raise ValueError(f'Invoice tab was not opened. Expected "{expected_title}"'
                             f' in page title, got: "{actual_title}"')
        self.logger.info(
            'Opened invoice tab: %s', invoice_page.page_url
        )
        return invoice_page, invoice_page.page_url

    def open_contact_sales(self):
        """Opens Contact Sales dialog."""

        self.click_element(self.contact_sales_button)
        self.is_element_present(
            CreditsPacksPageSelectors.CONTACT_SALES_MODAL.value, raise_error=True
        )
        self.logger.info('Opened Contact Sales dialog.')

    def close_contact_sales(self):
        """Closes Contact Sales dialog."""

        self.click_element(self.contact_sales_button)
        self.is_element_present(
            CreditsPacksPageSelectors.CONTACT_SALES_MODAL.value, raise_error=True
        )
        self.logger.info('Opened Contact Sales dialog.')
