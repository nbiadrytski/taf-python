"""Set env var DEBUG: pw:api for Playwright logs"""

import logging
from playwright._impl._api_types import (
    TimeoutError,
    Error
)

from utils.ui_constants import (
    DEFAULT_TIMEOUT,
    ELEM_NOT_FOUND_TIMEOUT,
    SCREENSHOTS_PATH,
    DOWNLOADS_PATH
)
from utils.selectors_enums import (
    HomePageSelectors,
    PendoTourSelectors,
    ModelsPageSelectors
)
from utils.errors import (
    WaitForElementTimeoutException,
    ElementAttributeTimeoutException,
    DownloadFileTimeoutException
)
from utils.helper_funcs import screenshot_name
from utils.data_enums import (
    PagePath,
    HtmlAttribute
)


NAVIGATE_LOG_MESSAGE = 'Navigated to %s'


class BasePage:

    def __init__(self, page, env_params):
        self.page = page
        self.app_host = env_params[0]
        self.logger = logging.getLogger(__name__)
        self.page.set_viewport_size({
            'width': 1920,
            'height': 1080
        })

    def wait_for_element(self, selector, timeout=DEFAULT_TIMEOUT,
                         screenshot=True, raise_error=True, help_text=''):
        """
        Waits for element to be visible within timeout ms.
        If timed out:
        1. Makes screenshot
        2. Logs error message
        3. Optionally raises custom WaitForElementTimeoutException

        Parameters
        ----------
        selector : str
            Element selector
        timeout : int
            Timeout looking for element in N ms
        raise_error : bool
            If to raise TimeoutError or not
        screenshot : bool
            If to make screenshot or not
        help_text : str
            Help text for debugging

        Returns
        -------
        element : playwright.sync_api._generated.ElementHandle
            Element
        """
        try:
            element = self.page.wait_for_selector(selector=selector,
                                                  timeout=timeout)
            self.logger.info('Found element by selector %s', selector)
            return element

        except TimeoutError as error:
            if screenshot:
                self.make_screenshot(selector)
            if raise_error:
                raise WaitForElementTimeoutException(selector, error, help_text)
            self.logger.error(
                'Did not find element by selector %s. %s. %s',
                selector, error, help_text)

    def navigate(self, path='', query_params='', wait_for_element=False,
                 selector='', timeout=DEFAULT_TIMEOUT):
        """
        Goes to page by provided path.
        Waits for page to load within timeout.
        Optionally accepts query params string.
        Optionally waits for element at the target page.

        Parameters
        ----------
        path : str
            Page path, e.g. /ai-platform
        query_params : str
            Query params string
        wait_for_element : bool
            If to wait for element at target page or not
        selector : str
            Element selector
        timeout : int
            Wait for target page to load or
            element at target page is visible
        """
        if query_params is None:
            url = f'{self.app_host}{path}?{query_params}'
        else:
            url = f'{self.app_host}{path}'

        self.page.goto(url, timeout=timeout)

        if wait_for_element:
            self.wait_for_element(selector, timeout)
            self.logger.info(NAVIGATE_LOG_MESSAGE, url)
        else:
            self.logger.info(NAVIGATE_LOG_MESSAGE, url)

    def navigate_to_ai_platform_page(self):
        """
        Goes to /ai-platform Home page using goto().
        Waits for Buy credits button to make sure the page is loaded.
        """
        self.navigate(
            PagePath.AI_PLATFORM_HOME.value,
            query_params='', wait_for_element=True,
            selector=HomePageSelectors.BUY_CREDITS.value,
            timeout=DEFAULT_TIMEOUT)

    def refresh_page(self):
        """Reloads current page using reload()"""

        self.page.reload()
        self.logger.info('%s page was reloaded', self.page_url)

    def enter_text(self, element, text):
        """
        Enters text into element field.

        Parameters
        ----------
        element : ElementHandle
            Element to enter text into
        text : str
            Text to enter
        """
        element.fill(text)
        self.logger.info('Entered %s into %s', text, element)

    def type_text(self, element, text, delay=100):
        """
        Types text into into a focused element field.

        Parameters
        ----------
        element : ElementHandle
            Element to type text into
        text : str
            Text to type
        delay : int
            Time to wait between key presses in milliseconds
        """
        element.type(text, delay=delay)
        self.logger.info('Typed "%s" into %s field', text, element)

    def click_element(self, element):
        """
        Clicks element.

        Parameters
        ----------
        element : ElementHandle
            Element to be clicked
        """
        try:
            element.click()
            self.logger.info('Clicked %s element', element)
        except TimeoutError as error:
            self.make_screenshot('click_failed')
            raise WaitForElementTimeoutException(element, error)

    def click_selector(self, selector):
        """
        Clicks selector.

        Parameters
        ----------
        selector : str
            Selector to be clicked
        """
        self.page.click(selector)
        self.logger.info('Clicked %s selector', selector)

    def is_element_clickable(self, selector, timeout=5000):
        """
        Returns True if element can be clicked within timeout, otherwise False.
        Playwright tries to click element until TimeoutError is raised.

        Parameters
        ----------
        selector : str
            Element selector
        timeout : int
            Timeout trying to click element in N ms

        Returns
        -------
        element : bool
            Is element clickable or not
        """
        log_message = 'Element with selector %s is {} clickable.'
        try:
            self.page.click(selector=selector, timeout=timeout)
            self.logger.info(log_message.format(''), selector)
            return True
        except TimeoutError:
            self.logger.info(log_message.format('not'), selector)
            return False

    def is_element_present(self, selector, timeout=ELEM_NOT_FOUND_TIMEOUT,
                           screenshot=True, raise_error=False, help_text=''):
        """
        If raise_error=True, waits for element for timeout ms.
        If element is found, then True is returned, else WaitForElementTimeoutException is raised.
        If raise_error=False, waits for element for timeout ms.
        If element is found, then True is returned, else False.

        Parameters
        ----------
        selector : str
            Element selector
        timeout : int
            Timeouts looking for element in N ms
        raise_error : bool
            If to raise WaitForElementTimeoutException or not
        screenshot : bool
            If to make screenshot or not
        help_text : str
            Help text for debugging

        Returns
        -------
        element : playwright.sync_api._generated.ElementHandle
            Element
        """
        if self.wait_for_element(
                selector, timeout, screenshot, raise_error, help_text) is None:
            self.logger.error(
                'Element with selector %s not found in %d ms. %s',
                selector, timeout, help_text)
            return False

        return True

    def get_attribute_value(self, selector, attribute_name,
                            timeout=ELEM_NOT_FOUND_TIMEOUT, raise_error=True):
        """
        Returns attribute value of element found by selector

        Parameters
        ----------
        selector : str
            Element selector
        attribute_name : str
            Html element attribute name
        timeout : float
            Timeout looking for element attribute value in N ms
        raise_error : bool
            If to raise ElementAttributeTimeoutException or not
            if element attribute value not found within timeout

        Returns
        -------
        attribute value : str
            Attribute value
        """
        try:
            value = self.page.get_attribute(selector, attribute_name,
                                            timeout=timeout)
            self.logger.debug(
                '"%s" attribute value of element with selector %s:'
                ' "%s"', attribute_name, selector, value)
            return value

        except TimeoutError as error:
            if raise_error:
                raise ElementAttributeTimeoutException(
                    attribute_name, selector, error)
            self.logger.error(
                '"%s" attribute value of element with selector %s'
                ' not found. %s', attribute_name, selector, error)

    def get_element_attribute_value(self, element, attribute_name):
        """
        Returns element attribute value.

        Parameters
        ----------
        element : ElementHandle
            Element
        attribute_name : str
            Html element attribute name

        Returns
        -------
        attribute value : str
            Attribute value
        """
        value = element.get_attribute(attribute_name)
        self.logger.debug('"%s" attribute value of element %s: "%s"',
                          attribute_name, element, value)
        return value

    def make_screenshot(self, selector_str=''):
        """
        If runs locally, creates screenshot in ui/screenshots/{selector_name_no_spaces}-{ts}.png
        In Jenkins: {selector_name_no_spaces}-{ts}.png

        Parameters
        ----------
        selector_str : str
            Element selector
        """
        name = screenshot_name(selector_str)
        local_path = f'{SCREENSHOTS_PATH}/{name}'
        log_message = 'Made screenshot: %s'

        try:  # for local runs
            self.page.screenshot(path=local_path)
            self.logger.info(log_message, local_path)

        except FileNotFoundError:  # for Jenkins runs
            self.page.screenshot(path=f'{name}')
            self.logger.info(log_message, name)

    def get_child_elements_by_selector(self, selector):
        """
        Waits for element.
        If element found, returns a list of child ElementHandle elements by passed element selector.

        Parameters
        ----------
        selector : str
            Element selector

        Returns
        -------
        child elements: list
            List of child ElementHandle elements
        """
        element = self.wait_for_element(selector)

        child_elements = element.query_selector_all('xpath=child::*')
        self.logger.info(
            'Element %s has %d child elements', element, len(child_elements)
        )
        return child_elements

    def get_child_elements(self, element):
        """
        Returns a list of child ElementHandle elements of passed element.

        Parameters
        ----------
        element : ElementHandle
            Element to get child elements from

        Returns
        -------
        child elements: list
            List of child ElementHandle elements
        """
        child_elements = element.query_selector_all('xpath=child::*')
        self.logger.info(
            'Element %s has %d child elements', element, len(child_elements)
        )
        return child_elements

    def get_inner_text(self, selector):
        """
        Returns inner text of element by selector.

        Parameters
        ----------
        selector : str
            Element selector

        Returns
        -------
        inner text: str
            Inner text of element
        """
        text = self.page.inner_text(selector)
        self.logger.info(
            'Selector "%s" inner text: "%s"', selector, text
        )
        return text

    def get_element_inner_text(self, element):
        """
        Returns inner text of ElementHandle element.

        Parameters
        ----------
        element : ElementHandle
            Element to get inner text from

        Returns
        -------
        inner text: str
            Inner text of element
        """
        text = element.inner_text()
        self.logger.info(
            'Element "%s" inner text: "%s"', element, text
        )
        return text

    def download_file(self, element, save_locally=True, timeout=300000,
                      raise_error=True):
        """
        Checks file is downloaded after clicking element which initiates download.
        Optionally saves file locally.
        Returns suggested file name for this download.

        Parameters
        ----------
        element : ElementHandle
            Element
        timeout : float
            Timeout downloading file in N ms
        save_locally : bool
            If to save file locally
        raise_error : bool
            If to raise DownloadFileTimeoutException

        Returns
        -------
        suggested_file_name: str
            Suggested filename for this download
        """
        try:
            with self.page.expect_download(timeout=timeout) as download_info:
                # Click element to start download
                self.click_element(element)
        except TimeoutError as error:
            self.make_screenshot('download_failed')
            if raise_error:
                raise DownloadFileTimeoutException(element, timeout, error)
            self.logger.error(
                'Timed out downloading file within %d ms after clicking %s element '
                'which initiated download. %s', timeout, element, error
            )
        download = download_info.value

        # Suggested filename for this download.
        # It is typically computed by browser
        # from Content-Disposition response header or 'download' attribute
        suggested_file_name = download.suggested_filename

        # Wait for the download process to complete.
        # failure() will return error string in case of any download failure
        download_failure = download.failure()
        if download_failure is not None:
            self.logger.error(
                'File %s download failure: %s', suggested_file_name, download_failure
            )
        self.logger.info(
            'Downloaded %s file', suggested_file_name
        )
        if save_locally:  # save file locally
            download_path = f'{DOWNLOADS_PATH}/{suggested_file_name}'
            try:
                # download to screenshots directory for local runs
                download.save_as(download_path)
                self.logger.info(
                    'Saved %s file to %s', suggested_file_name, download_path)
            except Error:  # playwright._impl._api_types.Error
                # for Jenkins downloads
                download.save_as(suggested_file_name)
                self.logger.info('Saved %s file', suggested_file_name)

        return suggested_file_name

    def upload_file(self, selector, file_name, file_path='',
                    default_directory=True):
        """
        Uploads file which is saved in default location:
        ui/screenshots directory or by provided file_path and file_name.
        'selector' param should point to <input> tag element which has 'type' attribute with value 'file'.

        Parameters
        ----------
        selector : str
            Element selector
        file_name : str
            File name with extension
        file_path : str
            Path to file (no trailing slash), e.g. ui/screenshots
        default_directory : bool
            If file for upload is located in default directory ui/screenshots
        """
        if default_directory:
            local_path = f'{DOWNLOADS_PATH}/{file_name}'
            # Local downloads are stored in ui/screenshots directory
            try:
                self.page.set_input_files(selector, local_path)
                self.logger.info('Uploaded %s', local_path)
            except FileNotFoundError:  # for Jenkins
                self.page.set_input_files(selector, file_name)
                self.logger.info('Uploaded %s', file_name)
        # for arbitrary path
        else:
            path = f'{file_path}/{file_name}'
            self.page.set_input_files(selector, path)
            self.logger.info('Uploaded %s', path)

    @property
    def page_url(self):
        """
        Returns page url.

        Returns
        -------
        url : str
            Page url
        """
        url = self.page.url
        self.logger.debug('Page url: %s', url)

        return url

    @property
    def page_title(self):
        """
        Returns page <title> tag value.

        Returns
        -------
        title : str
            Page <title> tag value
        """
        title = self.page.title()
        self.logger.info('Page title: %s', title)

        return title

    def open_new_tab(self, element, page):
        """
        Switches context to a new browser tab opened after clicking a button which initiates opening of a new tab.
        expect_page() returns EventContextManager.
        Variable tab is EventInfo class returned from the context manager.
        We can access the class using 'value' property which returns a Playwright Page object.
        Creates Page object based on the returned Playwright Page object
        which allows to use Page (DataPage, SignInPage, etc.) and parent BasePage actions.

        Parameters
        ----------
        element : ElementHandle
            Element to be clicked which initiates opening of a new tab
        page : Page object
            Type of new Page object, e.g. DataPage, SignInPage, etc.

        Returns
        -------
        new_page: Page object
            New Page object (DataPage, SignInPage, etc.)
        """
        with self.page.context.expect_page() as tab:
            self.click_element(element)

        new_page = page(tab.value, self.app_host)

        self.logger.info(
            'Opened page in a new tab: %s', new_page.page_url
        )
        return new_page

    def confirm_text_is_entered_into_element(self, element, expected_text,
                                             raise_error=True):
        """
        Confirms if text entered into element field is expected by checking 'value' attribute value.
        If actual_text != expected_text, either raises ValueError or logs a warning message.

        Parameters
        ----------
        element : ElementHandle
            Element field to enter text into
        expected_text : str
            Expected text
        raise_error : bool
            If to raise ValueError if actual_text != expected_text
        """
        actual_text = self.get_element_attribute_value(
            element, HtmlAttribute.VALUE.value
        )
        if actual_text != expected_text:
            if raise_error:
                raise ValueError(
                    f'Text entered into "{element}" element field '
                    f'must be "{expected_text}", got: "{actual_text}"')
            self.logger.warning(
                'Text entered into "%s" element must be "%s", got: "%s"',
                element, expected_text, actual_text)
        else:
            self.logger.debug(
                'Confirmed: "%s" text was entered into "%s" element field',
                actual_text, element)

    def close_pendo_tour_if_present(self):
        """If Pendo tour container is present, clicks No thanks button"""

        if self.is_element_present(
                PendoTourSelectors.TOUR_CONTAINER.value, screenshot=False
        ):
            self.click_selector(PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value)
            self.logger.info('Closed Pendo tour')
            # TODO: remove below once SELF-2716 is fixed
            if self.is_element_present(
                    PendoTourSelectors.TOUR_CONTAINER.value, screenshot=False
            ):
                self.click_selector(
                    PendoTourSelectors.CLOSE_TOUR_X_BUTTON.value)
                self.logger.info('Closed Pendo tour')
        else:
            self.logger.debug('No Pendo tour to close')

    def does_element_have_disabled_attribute(self, element):
        """
        Returns True if ElementHandle has 'disabled' attribute, otherwise returns False.

        Parameters
        ----------
        element : ElementHandle
            This element will be checked for 'disabled' attribute

        Returns
        -------
        does_element_have_disabled_attribute: bool
            If ElementHandle has 'disabled' attribute
        """
        if self.get_element_attribute_value(element, HtmlAttribute.DISABLED.value) is None:
            self.logger.debug(
                '%s has no "%s" attribute', element, HtmlAttribute.DISABLED.value)
            return False

        self.logger.debug(
            '%s has "%s" attribute', element, HtmlAttribute.DISABLED.value)
        return True

    def is_element_hidden(self, selector):
        """
        Returns whether the element is hidden, the opposite of visible.
        `selector` that does not match any elements is considered hidden.
        If there are multiple elements satisfying the selector, the first will be used.

        Parameters
        ----------
        selector : str
            Element selector

        Returns
        -------
        is_hidden: bool
            If element is hidden or not
        """
        log_message = 'Element with selector %s is {} hidden'

        if self.page.is_hidden(selector):
            self.logger.info(log_message.format(''), selector)
            return True

        self.logger.info(log_message.format('not'), selector)
        return False

    def get_text_content(self, selector):
        """
        Returns text content of element found by selector.

        Parameters
        ----------
        selector : str
            Element selector

        Returns
        -------
        text_content: str
            Element text content
        """
        text_content = self.page.text_content(selector)
        self.logger.info(
            'Element %s text content: %s', selector, text_content
        )
        return text_content

    def get_element_text_content(self, element):
        """
        Returns text content of ElementHandle element.

        Parameters
        ----------
        element : ElementHandle
            Element selector

        Returns
        -------
        text_content: str
            Element text content
        """
        text_content = element.text_content()
        self.logger.info(
            'Element %s text content: %s', element, text_content
        )
        return text_content

    def close_video(self):
        """
        Waits for Business Analyst Welcome video or video after clicking Start (modeling) button.
        Closes the video by clicking Close X button.
        """
        self.wait_for_element(ModelsPageSelectors.WELCOME_VIDEO.value)
        self.click_selector(ModelsPageSelectors.WELCOME_VIDEO_CLOSE_BUTTON.value)
        self.logger.info('Closed video')
