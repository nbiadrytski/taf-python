import logging
from os import environ

from utils.http_utils import (
    ResponseHandler,
    Request
)
from utils.helper_funcs import auth_header
from utils.constants import LOG_SEPARATOR
from utils.data_enums import (
    EnvVars,
    Envs
)


class ApiClient:
    """
    Aggregates api/v2, internal, DRAPб Auth0 and Docs Portal APIs.

    Parameters
    ----------
    env_params : function
        Returns a tuple of app2, DRAP and Auth0 hosts.
    session : function
        Returns <requests.sessions.Session> object. None by default.

    Attributes
    ----------
    app_host : str
        App host returned by env_params fixture
    dr_account_host : str
        DR Account Portal host returned by env_params fixture
    auth0_host : str
        Auth0 host returned by env_params fixture
    admin_auth_header : dict
        Authorization header with API key of a user with ADMIN_API_ACCESS flag turned on
    http_session : requests.sessions.Session
        HTTP session
    app_request : utils.http_utils.request.Request
        Inits request object with app host
    dr_account_request : utils.http_utils.request.Request
        Inits request object with DR Account Portal host
    auth0_request : utils.http_utils.request.Request
        Inits request object with Auth0 host
    user_api_key : str
        User API key
    auth0_api_v2_token : str
        Auth0 api/v2 token
    logger : logging.Logger
        Inits Logger object
    """

    def __init__(self, env_params, session=None):
        # hosts
        self.app_host = env_params[0]
        self.dr_account_host = env_params[1]
        self.auth0_host = env_params[2]
        if env_params[0] == Envs.STAGING.value:
            self.docs_host = Envs.DOCS_STAGING.value
        else:
            self.docs_host = Envs.DOCS_PROD.value

        if Envs.PROD.value in self.app_host:
            self.admin_auth_header = auth_header(
                environ[EnvVars.ADMIN_API_KEY_PROD.value])
        else:
            self.admin_auth_header = auth_header(
                environ[EnvVars.ADMIN_API_KEY_STAGING.value])

        # app2 request
        self.http_session = session
        self.app_request = Request(self.app_host)
        self.user_api_key = None

        # drap request
        self.dr_account_request = Request(self.dr_account_host)

        # auth0 request
        self.auth0_request = Request(self.auth0_host)
        self.auth0_api_v2_token = None

        # Docs Portal request
        self.docs_request = Request(self.docs_host)

        self.logger = logging.getLogger(__name__)

    def v2_api_admin_get_request(
            self, path='', query_params=None, allow_redirects=True,
            check_status_code=True
    ):
        """
        Performs admin user GET request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects, is_admin=True
        )
        return self._response(resp, check_status_code)

    def v2_api_get_request(
            self, path='', query_params=None, allow_redirects=True,
            check_status_code=True
    ):
        """
        Performs a test user GET request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects
        )
        return self._response(resp, check_status_code)

    def v2_api_admin_post_request(
            self, path='', request_body=None, files=None,
            check_status_code=True
    ):
        """
        Performs admin user POST request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        resp = self._perform_post_request(
            path, request_body, files=files, is_admin=True
        )
        return self._response(resp, check_status_code)

    def v2_api_post_request(
            self, path='', request_body=None, files=None,
            check_status_code=True
    ):
        """
        Performs a test user POST request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        resp = self._perform_post_request(
            path, request_body, files=files
        )
        return self._response(resp, check_status_code)

    def v2_api_admin_patch_request(
            self, path='', request_body=None, check_status_code=True
    ):
        """
        Performs admin user PATCH request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_patch_request(
            path, request_body, is_admin=True
        )
        return self._response(resp, check_status_code)

    def v2_api_patch_request(
            self, path='', request_body=None, check_status_code=True
    ):
        """
        Performs a test user PATCH request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_patch_request(path, request_body)
        return self._response(resp, check_status_code)

    def v2_api_admin_delete_request(
            self, path='', query_params=None, request_body=None,
            check_status_code=True
    ):
        """
        Performs admin user DELETE request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_delete_request(
            path, query_params, request_body, is_admin=True
        )
        return self._response(resp, check_status_code)

    def v2_api_delete_request(
            self, path='', query_params=None, request_body=None,
            check_status_code=True
    ):
        """
        Performs a test user DELETE request using api/v2.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_delete_request(
            path, query_params, request_body
        )
        return self._response(resp, check_status_code)

    def internal_api_post_request(
            self, path='', request_body=None, files=None,
            check_status_code=True
    ):
        """
        Performs a test user POST request using internal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        resp = self._perform_post_request(
            path, request_body, files=files, session=self.http_session
        )
        return self._response(resp, check_status_code)

    def internal_api_get_request(
            self, path='',
            query_params=None, allow_redirects=True, check_status_code=True
    ):
        """
        Performs GET request by a test user using internal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects, session=self.http_session
        )
        return self._response(resp, check_status_code)

    def auth0_get_request(
            self, path='', query_params=None, allow_redirects=True,
            check_status_code=True
    ):
        """
        Performs GET request using Auth0 API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects, is_auth0=True
        )
        return self._response(resp, check_status_code)

    def auth0_post_request(
            self, path='',
            request_body=None, files=None, check_status_code=True
    ):
        """
        Performs POST request using Auth0 API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        resp = self._perform_post_request(
            path, request_body, files=files, is_auth0=True
        )
        return self._response(resp, check_status_code)

    def auth0_delete_request(
            self, path='',
            query_params=None, request_body=None, check_status_code=True
    ):
        """
        Performs DELETE request using Auth0 API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by DELETE request
        """
        resp = self._perform_delete_request(
            path, query_params, request_body, is_auth0=True
        )
        return self._response(resp, check_status_code)

    def dr_account_get_request(
            self, path='',
            query_params=None, allow_redirects=True, check_status_code=True
    ):
        """
        Performs non-admin GET request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects, is_dr_account=True
        )
        return self._response(resp, check_status_code)

    def dr_account_admin_get_request(
            self, path='',
            query_params=None, allow_redirects=True, check_status_code=True
    ):
        """
        Performs admin GET request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects,
            is_dr_account=True, is_dr_account_admin=True
        )
        return self._response(resp, check_status_code)

    def dr_account_post_request(
            self, path='',
            request_body=None, files=None, check_status_code=True
    ):
        """
        Performs non-admin POST request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        resp = self._perform_post_request(
            path, request_body, files=files, is_dr_account=True
        )
        return self._response(resp, check_status_code)

    def dr_account_admin_post_request(
            self, path='',
            request_body=None, files=None, check_status_code=True
    ):
        """
        Performs admin POST request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        resp = self._perform_post_request(
            path, request_body,
            files=files, is_dr_account=True, is_dr_account_admin=True
        )
        return self._response(resp, check_status_code)

    def dr_account_delete_request(
            self, path='',
            query_params=None, request_body=None, check_status_code=True
    ):
        """
        Performs non-admin DELETE request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by DELETE request
        """
        resp = self._perform_delete_request(
            path, query_params, request_body, is_dr_account=True
        )
        return self._response(resp, check_status_code)

    def dr_account_admin_delete_request(
            self, path='',
            query_params=None, request_body=None, check_status_code=True
    ):
        """
        Performs admin DELETE request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by DELETE request
        """
        resp = self._perform_delete_request(
            path, query_params, request_body,
            is_dr_account=True, is_dr_account_admin=True
        )
        return self._response(resp, check_status_code)

    def dr_account_patch_request(
            self, path='', request_body=None, check_status_code=True):
        """
        Performs non-admin PATCH request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_patch_request(
            path, request_body, is_dr_account=True
        )
        return self._response(resp, check_status_code)

    def dr_account_admin_patch_request(
            self, path='', request_body=None, check_status_code=True
    ):
        """
        Performs admin PATCH request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_patch_request(
            path, request_body, is_dr_account=True, is_dr_account_admin=True
        )
        return self._response(resp, check_status_code)

    def dr_account_put_request(
            self, path='', request_body=None, check_status_code=True
    ):
        """
        Performs non-admin PUT request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_put_request(
            path, request_body, is_dr_account=True
        )
        return self._response(resp, check_status_code)

    def dr_account_admin_put_request(
            self, path='', request_body=None, check_status_code=True
    ):
        """
        Performs admin PUT request using DataRobot Account Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        resp = self._perform_put_request(
            path, request_body, is_dr_account=True, is_dr_account_admin=True
        )
        return self._response(resp, check_status_code)

    def docs_get_request(
            self, path='', query_params=None, allow_redirects=True,
            check_status_code=True
    ):
        """
        Performs GET request using Docs Portal API.

        Parameters
        ----------
        path : str
            Endpoint path, e.g. search. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        resp = self._perform_get_request(
            path, query_params, allow_redirects, is_docs=True
        )
        return self._response(resp, check_status_code)

    def predictions_api_post_request(
            self, host='', path='', datarobot_key=None, data=None,
            query_params=None, check_status_code=True
    ):
        """
        Performs a test user POST request using Request object.

        Parameters
        ----------
        host : str
            Prediction endpoint hostname, e.g. https://payasyougo.dynamic.orm.datarobot.com
        path : str
            Prediction endpoint path. Empty string by default
        datarobot_key : str
            Datarobot key: GET api/v2/predictionServers
        data : dict or list or bytes or file-like
            Dictionary, list of tuples, bytes, or file-like
            object to send in request body
        query_params: dict or bytes
            Dictionary or bytes to be sent in the query string
        check_status_code : bool
            If to check status code or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        headers = {'Authorization': f'Bearer {self.user_api_key}',
                   'datarobot-key': datarobot_key,
                   'Content-Type': 'text/plain; charset=UTF-8'}

        resp = Request(host).post_request(
            path=path, data=data, query_params=query_params, headers=headers
        )
        return self._response(resp, check_status_code)

    @staticmethod
    def assert_status_code(resp, expected_code, actual_code, message):
        assert actual_code == expected_code, \
            f'{message}. ' \
            f'Status code: {actual_code}. ' \
            f'Response: {ResponseHandler(resp).get_text()}'

    @staticmethod
    def get_response_header(resp, header_name):
        return ResponseHandler(resp).get_response_header(header_name)

    @staticmethod
    def get_location_header(resp):
        return ResponseHandler(resp).get_response_header('Location')

    @staticmethod
    def get_value_from_json_response(resp, key):
        return ResponseHandler(resp).get_json_key_value(key)

    @staticmethod
    def status_code(resp):
        return ResponseHandler(resp).get_status_code()

    @staticmethod
    def get_response_text(resp):
        return ResponseHandler(resp).get_text()

    @staticmethod
    def get_response_content(resp):
        return ResponseHandler(resp).get_content()

    @staticmethod
    def get_response_json(resp):
        return ResponseHandler(resp).get_json()

    @staticmethod
    def _assert_http_status_code(resp, code):
        response_handler = ResponseHandler(resp)
        status_code = response_handler.get_status_code()
        assert status_code == code, \
            f'Non-200 status code returned: {status_code}. ' \
            f'Response: {response_handler.get_text()}'

    def _log_http_response(self, resp):
        response_handler = ResponseHandler(resp)
        self.logger.debug(
            'RESPONSE HEADERS: %s', response_handler.get_response_headers())
        self.logger.debug(
            'RESPONSE BODY: %s%s', response_handler.get_text(), LOG_SEPARATOR)

    def _check_and_log_response(self, resp, status_code):
        self._assert_http_status_code(resp, status_code)
        self._log_http_response(resp)

    def _response(self, resp, check_status_code):
        if check_status_code:
            self._check_and_log_response(resp, status_code=200)
            return resp
        self._log_http_response(resp)
        return resp

    def _set_auth_header(
            self, is_admin, is_dr_account, is_dr_account_admin, is_auth0,
            is_docs
    ):
        if is_admin:
            return self.admin_auth_header
        if is_dr_account:
            if not is_dr_account_admin:
                return auth_header(self.auth0_auth_token)
            return auth_header(self.admin_auth0_token)
        if is_auth0:
            return auth_header(self.auth0_api_v2_token)
        if is_docs:
            return {'Caller': 'Docs Portal E2E API tests'}

        return auth_header(self.user_api_key)

    def _perform_get_request(
            self, path, query_params, allow_redirects,
            session=None, is_admin=False,
            is_dr_account=False, is_dr_account_admin=False,
            is_auth0=False,
            is_docs=False
    ):
        headers = self._set_auth_header(
            is_admin, is_dr_account, is_dr_account_admin, is_auth0, is_docs
        )
        if is_dr_account:
            return self.dr_account_request.get_request(
                session, path, query_params, headers, allow_redirects
            )
        if is_auth0:
            return self.auth0_request.get_request(
                session, path, query_params, headers, allow_redirects
            )
        if is_docs:
            return self.docs_request.get_request(
                session, path, query_params, headers, allow_redirects)

        return self.app_request.get_request(
            session, path, query_params, headers, allow_redirects)

    def _perform_post_request(
            self, path, request_body,
            session=None, files=None, is_admin=False,
            is_dr_account=False, is_dr_account_admin=False,
            is_auth0=False,
            is_docs=False
    ):
        headers = self._set_auth_header(
            is_admin, is_dr_account, is_dr_account_admin, is_auth0, is_docs
        )
        if is_dr_account:
            return self.dr_account_request.post_request(
                session, path, request_body, headers, files
            )
        if is_auth0:
            return self.auth0_request.post_request(
                session, path, request_body, headers, files)

        return self.app_request.post_request(
            session, path, request_body, headers, files)

    def _perform_patch_request(
            self, path, request_body, session=None, is_admin=False,
            is_dr_account=False, is_dr_account_admin=False,
            is_auth0=False, is_docs=False
    ):
        headers = self._set_auth_header(
            is_admin, is_dr_account, is_dr_account_admin, is_auth0, is_docs
        )
        if is_dr_account:
            return self.dr_account_request.patch_request(
                session, path, request_body, headers
            )
        if is_auth0:
            return self.auth0_request.patch_request(
                session, path, request_body, headers)

        return self.app_request.patch_request(
            session, path, request_body, headers)

    def _perform_put_request(
            self, path, request_body, session=None, is_admin=False,
            is_dr_account=False, is_dr_account_admin=False,
            is_auth0=False, is_docs=False
    ):
        headers = self._set_auth_header(
            is_admin, is_dr_account, is_dr_account_admin, is_auth0, is_docs
        )
        if is_dr_account:
            return self.dr_account_request.put_request(
                session, path, request_body, headers
            )
        if is_auth0:
            return self.auth0_request.put_request(
                session, path, request_body, headers)

        return self.app_request.put_request(
            session, path, request_body, headers)

    def _perform_delete_request(
            self, path, query_params, request_body, session=None,
            is_admin=False,
            is_dr_account=False, is_dr_account_admin=False,
            is_auth0=False,
            is_docs=False
    ):
        headers = self._set_auth_header(
            is_admin, is_dr_account, is_dr_account_admin, is_auth0, is_docs
        )
        if is_dr_account:
            return self.dr_account_request.delete_request(
                session, path, query_params, headers, request_body
            )
        if is_auth0:
            return self.auth0_request.delete_request(
                session, path, query_params, headers, request_body)

        return self.app_request.delete_request(
            session, path, query_params, headers)
