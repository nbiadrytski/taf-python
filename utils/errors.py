class Error(Exception):
    """Base custom errors class."""

    def __str__(self):
        return f'{self.message}'


class UnsupportedEnvException(Error):
    """Raised if invalid --app_host value or no value is passed as command line arg."""

    def __init__(self, env, supported_envs):
        self.message = f'\n"{env}" is not a supported environment.' \
                       f'\n Supported environments: {supported_envs}.'


class NoHostArgException(Error):
    """
    Raised if --app_host, --dr_account_host or --auth0_host command line arg
    was not passed when starting tests."""

    def __init__(self, env, host_arg):
        self.message = f'\nCommand line arg "{host_arg}" is missing. ' \
                       f'App host is {env}.'


class NoApiKeyException(Error):
    """Raised if --api_key command line arg was not passed when starting tests."""

    def __init__(self, api_key):
        self.message = f'\nCommand line arg "--api_key" is missing. ' \
                       f'API key is {api_key}.'


class FailedToRegisterDrAccountPortalUserException(Error):
    """Raised if DataRobot Account Portal user registration failed
    and there was no portalId key returned in response"""

    def __init__(self, username, resp):
        self.message = f'User {username} was not registered into DataRobot Account Portal. ' \
                       f'Response: {resp}'


class DeployedModelNotReplacedException(Error):
    """Raised if deployed model was not replaced as desired."""

    def __init__(self, app_client, deployment_id, replaced_count):
        app_client.v2_delete_deployment(deployment_id)

        self.message = f'\nModel with deployment_id {deployment_id} ' \
                       f'was not replaced {replaced_count} times.'


class ModelJobNotDoneException(Error):
    """Raised if model job did not finish."""

    def __init__(self, project_id, model_name):
        self.message = f'\n{model_name} model job for project {project_id} ' \
                       f'did not finish in given time.'


class ModelInvalidForReplacementException(Error):
    """Raised if model is invalid for replacement."""

    def __init__(self, project_id, model_name):
        self.message = f'\n{model_name} model job for project {project_id} ' \
                       f'did not finish in given time.'


class WaitForElementTimeoutException(Error):
    """Raised if UI element is not found withing timeout."""

    def __init__(self, selector, error, help_text=''):
        self.message = f'{help_text}. Did not find element by selector {selector}.' \
                       f' {error}.'


class TourNotResetException(Error):
    """Raised if Pendo tour was not reset in N number of rounds."""

    def __init__(self, user_id, rounds):
        self.message = f'Pendo tour for user {user_id} ' \
                       f'was not reset in {rounds} rounds.'


class ElementIsPresentException(Error):
    """Raised if element is unexpectedly present."""

    def __init__(self, selector):
        self.message = f'Element with {selector} is present, ' \
                       f'but should be absent.'


class ElementIsAbsentException(Error):
    """Raised if element is unexpectedly absent."""

    def __init__(self, selector, help_text=''):
        self.message = f'Element with {selector} is absent, ' \
                       f'but should be present. {help_text}'


class ElementIsClickableException(Error):
    """Raised if element is can be clicked."""

    def __init__(self, selector, help_text=''):
        self.message = f'Element with {selector} is clickable, ' \
                       f'but should be not. {help_text}'


class ElementIsHiddenException(Error):
    """Raised if element is hidden."""

    def __init__(self, selector, help_text=''):
        self.message = f'Element with {selector} is hidden, ' \
                       f'but should be not. {help_text}'


class ElementIsVisibleException(Error):
    """Raised if element is visible."""

    def __init__(self, selector, help_text=''):
        self.message = f'Element with {selector} is visible, ' \
                       f'but should be not. {help_text}'


class ElementAttributeTimeoutException(Error):
    """Raised if attribute of element is not found within timeout."""

    def __init__(self, attribute, selector, error):
        self.message = f'"{attribute}" attribute value ' \
                       f'of element with {selector} selector not found. {error}'


class DownloadFileTimeoutException(Error):
    """Raised if file is not downloaded within timeout."""

    def __init__(self, element, timeout, error):
        self.message = f'file was not downloaded within {timeout} ms' \
                       f' after clicking {element} element' \
                       f' which initiated download. {error}'
