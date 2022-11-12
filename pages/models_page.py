from time import sleep

from pages.base_page import BasePage
from utils.selectors_enums import (
    ModelsPageSelectors,
    DeploymentsPageSelectors
)
from utils.constants import TIMEOUT_MESSAGE
from utils.ui_constants import WAIT_FOR_MODEL_TIMEOUT
from utils.helper_funcs import (
    time_left,
    time,
    get_id_from_url
)
from utils.data_enums import HtmlAttribute


class ModelsPage(BasePage):
    def __init__(self, page, env_params):
        super().__init__(page, env_params)

    @property
    def predict_tab(self):
        return self.wait_for_element(
            ModelsPageSelectors.MODEL_DETAILS_PREDICT_TAB.value)

    @property
    def deploy_tab(self):
        return self.wait_for_element(
            ModelsPageSelectors.MODEL_DETAILS_DEPLOY_TAB.value)

    @property
    def deploy_model_button(self):
        return self.wait_for_element(
            # Model detailed view
            ModelsPageSelectors.DEPLOY_MODEL_BUTTON.value)

    @property
    def automodel_button(self):
        return self.wait_for_element(
            ModelsPageSelectors.AUTOMODEL_BUTTON.value)

    @property
    def random_forest_classifier_gini_model_title(self):
        return self.wait_for_element(
            ModelsPageSelectors.RANDOM_FOREST_CLASSIFIER_GINI_MODEL.value,
            timeout=WAIT_FOR_MODEL_TIMEOUT)

    @property
    def boosted_trees_classifier_model_title(self):
        return self.wait_for_element(
            ModelsPageSelectors.GRADIENT_BOOSTED_TREES_CLASSIFIER_MODEL.value,
            timeout=WAIT_FOR_MODEL_TIMEOUT)

    @property
    def close_welcome_video_button(self):
        return self.wait_for_element(
            ModelsPageSelectors.WELCOME_VIDEO_CLOSE_BUTTON.value)

    def expand_model(self, model_element):
        self.click_element(model_element)
        self.wait_for_element(ModelsPageSelectors.MODEL_DETAILS_PREDICT_TAB.value)

        model_id = get_id_from_url(self.page_url, index=2)
        self.logger.info('Expanded modelId %s "%s"', model_id, model_element)

        return model_id

    def poll_for_predict_tab_enabled(self, timeout_period=8, poll_interval=5):
        """
        Polls for 'Predict' tab at model detailed view to be enabled by checking
        its class attribute doesn't contain 'disabled' string.
        """
        timeout = time() + 60 * timeout_period
        while True:
            class_attribute_value = self.get_attribute_value(
                ModelsPageSelectors.MODEL_DETAILS_PREDICT_TAB.value, HtmlAttribute.CLASS.value
            )
            self.logger.info(
                'Polling for Predict tab to be enabled. Time left %s', time_left(timeout)
            )
            if time() > timeout:
                raise TimeoutError(
                    TIMEOUT_MESSAGE.format(
                    'Predict tab', 'to be enabled', class_attribute_value, timeout_period)
                )
            if HtmlAttribute.DISABLED.value not in class_attribute_value:
                self.logger.info(
                    'Predict tab is enabled. Class attribute value: "%s"', class_attribute_value
                )
                break

            sleep(poll_interval)

    def deploy_model(self):
        """
        Deploys model from Predict -> Deploy tab:
        1. Click Deploy model button from model expanded view
        2. Click Create deployment button from deployments/new/configure?packageId={package_id} page
        """
        self.click_element(self.deploy_model_button)

        self.wait_for_element(
            DeploymentsPageSelectors.CREATE_DEPLOYMENT_BUTTON.value, timeout=400000)
        self.click_selector(DeploymentsPageSelectors.CREATE_DEPLOYMENT_BUTTON.value)

        self.wait_for_element(
            DeploymentsPageSelectors.REVIEW_MODAL_CREATE_DEPLOYMENT_BUTTON.value,
            timeout=400000)
        self.click_selector(
            DeploymentsPageSelectors.REVIEW_MODAL_CREATE_DEPLOYMENT_BUTTON.value)

        self.wait_for_element(
            DeploymentsPageSelectors.DEPLOYMENT_CREATED_TILE.value, timeout=400000)

        deployment_id = get_id_from_url(self.page_url, index=1)

        self.logger.info('Model is deployed. Deployment Id: %s', deployment_id)

        return deployment_id

    def poll_for_automodel_button_enabled(
            self, selector, timeout_period=8, poll_interval=2):
        """Polls for Automodel button to be enabled by checking it doesn't have 'disabled' attribute"""

        timeout = time() + 60 * timeout_period
        while True:
            disable_attribute = self.get_attribute_value(
                selector, HtmlAttribute.DISABLED.value, raise_error=False
            )
            self.logger.info(
                'Polling for Automodel button to be enabled. Time left %s', time_left(timeout)
            )
            if time() > timeout:
                raise TimeoutError(TIMEOUT_MESSAGE.format(
                    'Automodel button', 'to be enabled',
                    f'disabled attribute value: {disable_attribute}', timeout_period)
                )
            if disable_attribute is None:
                self.logger.info('Automodel button is enabled.')
                break

            sleep(poll_interval)

    def deploy_automodel(self, timeout_period=8, poll_interval=2):
        """
        Deploys Automodel once the button is enabled.
        Retrieves and returns deployment_id from href attribute.
        """
        self.poll_for_automodel_button_enabled(
            ModelsPageSelectors.AUTOMODEL_BUTTON.value, timeout_period, poll_interval)
        # Click Automodel button
        self.click_element(self.automodel_button)

        # Wait for Automodel to be deployed
        self.wait_for_element(
            ModelsPageSelectors.AUTOMODEL_DEPLOYED_BUTTON.value, timeout=200000, raise_error=True
        )
        href_value = self.get_attribute_value(
            ModelsPageSelectors.AUTOMODEL_DEPLOYED_BUTTON.value, HtmlAttribute.HREF.value
        )
        # Get deployment_id from href, e.g.: '/deployments/id'
        deployment_id = href_value.replace('/deployments/', '')

        self.logger.info('Deployed Automodel. Deployment Id: %s', deployment_id)

    def close_welcome_video(self):
        """
        Waits for Welcome video after clicking Start (modeling) button.
        Closes the video by clicking Close X button.
        """
        self.wait_for_element(ModelsPageSelectors.WELCOME_VIDEO.value)
        self.click_element(self.close_welcome_video_button)
        self.logger.info('Closed Welcome video')
