from time import sleep
from pages.base_page import BasePage
from utils.selectors_enums import (
    DeploymentsPageSelectors,
    AppsPageSelectors
)
from utils.helper_funcs import (
    time_left,
    time
)
from utils.data_enums import HtmlAttribute
from utils.constants import TIMEOUT_MESSAGE
from utils.ui_constants import COMPUTE_PREDICTIONS_BUTTON
from utils.errors import ElementIsAbsentException


class DeploymentsPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def predictions_tab(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.PREDICTIONS_TAB.value)

    @property
    def download_sample_data_button(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.DOWNLOAD_SAMPLE_DATA_BUTTON.value)

    @property
    def choose_prediction_file_button(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.CHOOSE_PREDICTION_FILE_BUTTON.value)

    @property
    def compute_predictions_button(self):
        # Compute and download predictions button
        # Disabled until prediction dataset is uploaded
        return self.wait_for_element(
            DeploymentsPageSelectors.COMPUTE_DOWNLOAD_PREDICTIONS_BUTTON.value)

    @property
    def splash_modal_close_button(self):
        # Close X button at top right corner of MLOps splash modal
        return self.wait_for_element(
            DeploymentsPageSelectors.SPLASH_MODAL_CLOSE_BUTTON.value)

    @property
    def automodel_deployed_flag(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.AUTOMODEL_DEPLOYED_FLAG.value)

    @property
    def deployment_actions_menu(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.DEPLOYMENT_ACTIONS_MENU.value)

    @property
    def create_app_button(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.CREATE_APP_BUTTON.value)

    @property
    def deploy_app_button(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.DEPLOY_APP_BUTTON.value)

    @property
    def what_if_app(self):
        return self.wait_for_element(
            DeploymentsPageSelectors.WHAT_IF_APP.value)

    def download_predictions_sample_dataset(self):
        """
        Downloads sample prediction dataset from deployments/{deployment_id}/predictions/make-predictions page.
        Returns downloaded file name.
        """
        file_name = self.download_file(self.download_sample_data_button)
        self.logger.info(
            'Downloaded predictions sample dataset %s', file_name
        )
        return file_name

    def upload_predictions_dataset(self, file_name,
                                   max_retries=5, wait_interval=10):
        """
        Tries to upload prediction dataset from deployments/{deployment_id}/predictions/make-predictions page.
        If dataset is not uploaded ('Compute and download predictions' button is still disabled in this case),
        uploading is started again until max_retries limit is reached.
        Additionally, if 'Compute and download predictions' button is disabled,
        checking if Predictions error alert has appeared. The most common one is:
        'You have exceeded your limit on total modeling API requests. Try again in N seconds.'
        """
        retry = 0
        while True:
            retry = retry + 1

            self.click_element(self.choose_prediction_file_button)
            self.upload_file(
                DeploymentsPageSelectors.
                    UPLOAD_SAMPLE_DATA_FILE_INPUT.value, file_name)

            if retry >= max_retries:
                self.make_screenshot('prediction_dataset_not_uploaded')
                raise Exception(
                    f'Predictions dataset {file_name} was not uploaded.'
                    f' Tried {max_retries} times.')

            if self.is_compute_predictions_button_enabled():
                sleep(5)
                # wait and then refresh the page if predictions error alert is present
                if self.is_element_present(
                        DeploymentsPageSelectors.PREDICTIONS_ERROR_ALERT.value,
                        timeout=9000,
                        screenshot=False
                ):
                    self.logger.warning(
                        'Predictions error alert. Wait for %d seconds and'
                        ' refresh the page', wait_interval
                    )
                    sleep(wait_interval)
                    self.refresh_page()
                else:
                    self.logger.info(
                        'Uploaded predictions dataset %s without errors',
                        file_name
                    )
                    break
            else:
                self.refresh_page()

    def compute_and_download_predictions(self):
        """
        Clicks 'Compute and download predictions' button which initiates predictions file download process.
        Waits for a small icon at predictions card which appears when predictions are computed and downloaded.
        Returns downloaded file name.
        """
        file_name = self.download_file(self.compute_predictions_button)
        self.wait_for_element(
            DeploymentsPageSelectors.DOWNLOAD_FINISHED_PREDICTIONS_BUTTON.value
        )
        self.logger.info(
            'Predictions are computed and %s downloaded', file_name
        )
        return file_name

    def is_compute_predictions_button_enabled(self,
                                              timeout_period=5,
                                              poll_interval=5,
                                              raise_error=False):
        """
        Polls for "Compute and download predictions" button to be enabled
        at deployments/{deployment_id}/predictions/make-predictions page.
        Returns True if the button is enabled, otherwise ether returns False or raises TimeoutError.
        If get_attribute_value() returns None, this means element has no 'disabled' attribute --> element is enabled.
        If 'Compute and download predictions' button is enabled, this means predictions dataset has been uploaded.
        """
        timeout = time() + 60 * timeout_period
        while True:
            disabled_attribute = self.get_attribute_value(
                DeploymentsPageSelectors.
                    COMPUTE_DOWNLOAD_PREDICTIONS_BUTTON.value,
                HtmlAttribute.DISABLED.value,
                raise_error=False
            )
            self.logger.info(
                'Polling for %s to be enabled. Time left %s.',
                COMPUTE_PREDICTIONS_BUTTON, time_left(timeout)
            )
            if time() > timeout:
                if raise_error:
                    self.make_screenshot(
                        DeploymentsPageSelectors.
                            COMPUTE_DOWNLOAD_PREDICTIONS_BUTTON.value
                    )
                    raise TimeoutError(
                        f'{COMPUTE_PREDICTIONS_BUTTON} did not get enabled'
                        f' in {timeout_period} minutes.')

                self.logger.error(
                    '%s did not get enabled in %d minutes',
                    COMPUTE_PREDICTIONS_BUTTON, timeout_period
                )
                self.make_screenshot(
                    DeploymentsPageSelectors.
                        COMPUTE_DOWNLOAD_PREDICTIONS_BUTTON.value
                )
                return False

            if disabled_attribute is None:
                self.logger.info(
                    '%s is enabled.', COMPUTE_PREDICTIONS_BUTTON
                )
                return True

            sleep(poll_interval)

    def close_mlops_splash_modal(self, raise_error=False):
        """
        Closes MLOps Splash Modal if present.
        Otherwise either raises ElementIsAbsentException or logs a warning message.
        """
        if self.is_element_present(
                DeploymentsPageSelectors.SPLASH_MODAL_WELCOME_PAGE.value, screenshot=False):
            self.click_element(self.splash_modal_close_button)
            self.logger.info('Closed MLOps Splash Modal')
        else:
            if raise_error:
                raise ElementIsAbsentException(
                    DeploymentsPageSelectors.SPLASH_MODAL_WELCOME_PAGE.value,
                    'MLOps Splash Modal must be present!'
                )
            self.logger.warning('MLOps Splash Modal is absent')

    def expand_automodel_deployment(self):
        """
        Clicks a small flag icon at Automodel deployment to expand the deployment.
        Waits for Deployment created tile to confirm deployment is expanded.
        """
        self.click_element(self.automodel_deployed_flag)
        self.wait_for_element(
            DeploymentsPageSelectors.DEPLOYMENT_CREATED_TILE.value)

    def open_deployment_actions_menu(self):
        # Click deployment actions menu button
        self.click_element(self.deployment_actions_menu)
        # Wait for Delete button at the expanded menu
        self.wait_for_element(
            DeploymentsPageSelectors.DELETE_DEPLOYMENT_BUTTON.value)

    def create_app(self, app_selector,
                   timeout_period=10, poll_interval=2):
        """
        Clicks Create Application option element from deployment actions menu.
        Selects the app by app_selector and confirms the app is selected.
        Confirms if 'Deploy' app button is enabled and clicks it.
        Polls for app to be deployed by checking
        if 'class' attribute of 'Open' app button doesn't contain 'disabled' string.
        Returns app url retrieved from 'Open' app button 'href' attribute.
        """
        self.click_element(self.create_app_button)

        self.click_selector(app_selector)
        self.poll_for_app_selected(app_selector)

        self._assert_deploy_button_enabled()
        self.click_element(self.deploy_app_button)

        timeout = time() + 60 * timeout_period
        while True:
            class_attribute = self.get_attribute_value(
                AppsPageSelectors.OPEN_APP_BUTTON.value,
                HtmlAttribute.CLASS.value
            )
            self.logger.info(
                'Polling for App with %s selector to be deployed.'
                ' Time left %s', app_selector, time_left(timeout)
            )
            if time() > timeout:
                raise TimeoutError(
                    TIMEOUT_MESSAGE.format(
                        f'App with selector {app_selector}',
                        'to be deployed',
                        f'class attribute value: {class_attribute}',
                        timeout_period)
                )
            if HtmlAttribute.DISABLED.value not in class_attribute:
                app_url = self.get_attribute_value(
                    AppsPageSelectors.OPEN_APP_BUTTON.value,
                    HtmlAttribute.HREF.value
                )
                self.logger.info(
                    'App with %s selector is deployed. App url: %s',
                    app_selector, app_url
                )
                return app_url

            sleep(poll_interval)

    def poll_for_app_selected(self,
                              app_selector,
                              timeout_period=2,
                              poll_interval=1):
        """
        Polls for App to be selected at Create Application modal.
        'class' attribute should contain 'selected' string.
        """
        expected_value = 'selected'
        timeout = time() + 60 * timeout_period
        while True:
            class_attribute = self.get_attribute_value(
                app_selector, HtmlAttribute.CLASS.value
            )
            self.logger.info(
                'Polling for App with %s selector to be %s.'
                ' Time left %s',
                app_selector, expected_value, time_left(timeout)
            )
            if time() > timeout:
                raise TimeoutError(
                    TIMEOUT_MESSAGE.format(
                        f'App with selector {app_selector}', 'to be selected',
                        f'class attribute value: {class_attribute}',
                        timeout_period)
                )
            if expected_value in class_attribute:
                self.logger.info(
                    'App with %s selector is selected.',
                    app_selector
                )
                break

            sleep(poll_interval)

    def _assert_deploy_button_enabled(self):
        """'Deploy' app button must be enabled."""
        disabled_attribute = self.get_attribute_value(
            DeploymentsPageSelectors.DEPLOY_APP_BUTTON.value,
            HtmlAttribute.DISABLED.value
        )
        if disabled_attribute is not None:
            raise ValueError(
                f'"Deploy" app button must be enabled,'
                f' but "{HtmlAttribute.DISABLED.value}" attribute has value: '
                f'"{disabled_attribute}'
            )
        self.logger.debug('"Deploy" app button is enabled')
