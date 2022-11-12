from utils.constants import USER_PASSWORD
from pages.base_page import BasePage
from utils.selectors_enums import (
    SignInPageSelectors,
    TopMenuSelectors,
    DrapTopMenuSelectors
)
from utils.data_enums import Envs


class SignInPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def email_field(self):
        if Envs.PROD.value in self.app_host:
            return self.auth0_email_field
        return self.wait_for_element(
            SignInPageSelectors.STAGING_EMAIL_FIELD.value)

    @property
    def auth0_email_field(self):
        return self.wait_for_element(
            SignInPageSelectors.APP2_EMAIL_FIELD.value)

    @property
    def password_field(self):
        if Envs.PROD.value in self.app_host:
            return self.auth0_password_field
        return self.wait_for_element(
            SignInPageSelectors.STAGING_PASSWORD_FIELD.value)

    @property
    def auth0_password_field(self):
        return self.wait_for_element(
            SignInPageSelectors.APP2_PASSWORD_FIELD.value)

    @property
    def sign_in_button(self):
        if Envs.PROD.value in self.app_host:
            return self.auth0_sign_in_button
        return self.wait_for_element(
            SignInPageSelectors.STAGING_SIGN_IN_BUTTON.value)

    @property
    def auth0_sign_in_button(self):
        return self.wait_for_element(
            SignInPageSelectors.APP2_SIGN_IN_BUTTON.value)

    def sign_in(self, username, is_auth0=False):
        if Envs.PROD.value in self.app_host:
            # Wait until Sign In with Google button is loaded
            # otherwise clicking Sign In button fails
            self.wait_for_element(
                SignInPageSelectors.APP2_GOOGLE_SIGN_IN_BUTTON.value)

        self.enter_text(self.email_field, username)
        # Clicks CONTINUE button from pre-sign in page
        self.click_element(self.sign_in_button)

        if is_auth0:
            self.wait_for_element(
                SignInPageSelectors.APP2_GOOGLE_SIGN_IN_BUTTON.value
            )
            self.enter_text(self.auth0_password_field, USER_PASSWORD)
            self.click_element(self.auth0_sign_in_button)
        else:
            self.enter_text(self.password_field, USER_PASSWORD)
            self.click_element(self.sign_in_button)

        # Wait for app2/staging DataRobot logo
        self.wait_for_element(TopMenuSelectors.DR_LOGO.value)

        self.logger.info('User %s signed in', username)

    def auth0_sign_in(self, username, drap=True):
        """
        Signs in user from Auth0 sign in page.
        Auth0 dev: https://datarobotdev.auth0.com/login.
        Auth0 prod: https://account.datarobot.com/login.
        If user needs to sign into DRAP (e.g. after clicking 'Full Usage Details' link from Credits Usage widget),
        then waits for DRAP DR logo element.
        Otherwise, waits for App2/Staging DR logo element.
        """
        # Wait until Sign In with Google button is loaded
        # otherwise clicking Sign In button fails
        self.wait_for_element(
            SignInPageSelectors.APP2_GOOGLE_SIGN_IN_BUTTON.value)

        self.enter_text(self.auth0_email_field, username)
        self.enter_text(self.auth0_password_field, USER_PASSWORD)
        self.click_element(self.auth0_sign_in_button)

        if drap:
            # Wait for DRAP DataRobot logo
            self.wait_for_element(
                DrapTopMenuSelectors.DR_LOGO.value)
        else:
            # Wait for app2/staging DataRobot logo
            self.wait_for_element(
                TopMenuSelectors.DR_LOGO.value)

        self.logger.info('User %s signed in', username)
