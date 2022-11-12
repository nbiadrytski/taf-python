from urllib.parse import urljoin
import logging

import requests

from utils.constants import LOG_SEPARATOR


class Request:
    """
    Wrapper around requests module.

    Parameters
    ----------
    host : str
        App hostname

    Attributes
    ----------
    host : str
         App hostname
    logger : logging.Logger
        Inits Logger object
    """

    def __init__(self, host):
        self.host = host
        self.logger = logging.getLogger(__name__)

    def get_request(self,
                    session=None,
                    path='',
                    query_params=None,
                    headers=None,
                    allow_redirects=True):
        """
        Performs HTTP GET request.

        Parameters
        ----------
        session : requests.sessions.Session
            HTTP session object. None by default
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        headers : dict
            Request headers, e.g. {'key': 'value'}. None by default
        allow_redirects : bool
            If to allow http redirects or not. True by default

        Returns
        -------
        response : requests.models.Response
            Response returned by GET request
        """
        self._log_request_params_and_headers(query_params, headers)
        if session:
            return session.get(
                url=urljoin(self.host, path),
                params=query_params,
                headers=headers,
                allow_redirects=allow_redirects,
                verify=False)
        return requests.get(
            url=urljoin(self.host, path),
            params=query_params,
            headers=headers,
            allow_redirects=allow_redirects,
            verify=False)

    def post_request(self,
                     session=None,
                     path='',
                     request_body=None,
                     headers=None,
                     files=None,
                     data=None,
                     query_params=None):
        """
        Performs HTTP POST request.

        Parameters
        ----------
        session : requests.sessions.Session
            HTTP session object. None by default
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        headers : dict
            Request headers, e.g. {'key': 'value'}. None by default
        files : dict
            Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional
        headers to add for the file.
        data : dict or list or file-like object
            Dictionary, list of tuples, bytes, or file-like object to send in request body
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value). None by default

        Returns
        -------
        response : requests.models.Response
            Response returned by POST request
        """
        self._log_request_body_and_headers(request_body, headers)
        if session:
            return session.post(url=urljoin(self.host, path),
                                json=request_body,
                                headers=headers,
                                files=files,
                                data=data,
                                params=query_params)
        return requests.post(url=urljoin(self.host, path),
                             json=request_body,
                             headers=headers,
                             files=files,
                             data=data,
                             params=query_params)

    def patch_request(self,
                      session=None,
                      path='',
                      request_body=None,
                      headers=None):
        """
        Performs HTTP PATCH request.

        Parameters
        ----------
        session : requests.sessions.Session
            HTTP session object. None by default
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        headers : dict
            Request headers, e.g. {'key': 'value'}. None by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PATCH request
        """
        self._log_request_body_and_headers(request_body, headers)
        if session:
            return session.patch(
                url=urljoin(self.host, path),
                json=request_body,
                headers=headers)
        return requests.patch(url=urljoin(self.host, path),
                              json=request_body,
                              headers=headers)

    def put_request(self,
                    session=None,
                    path='',
                    request_body=None,
                    headers=None):
        """
        Performs HTTP PUT request.

        Parameters
        ----------
        session : requests.sessions.Session
            HTTP session object. None by default
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default
        headers : dict
            Request headers, e.g. {'key': 'value'}. None by default

        Returns
        -------
        response : requests.models.Response
            Response returned by PUT request
        """
        self._log_request_body_and_headers(request_body, headers)
        if session:
            return session.put(
                url=urljoin(self.host, path),
                json=request_body,
                headers=headers)
        return requests.put(url=urljoin(self.host, path),
                              json=request_body,
                              headers=headers)

    def delete_request(self,
                       session=None,
                       path='',
                       query_params=None,
                       headers=None,
                       request_body=None):
        """
        Performs HTTP DELETE request.

        Parameters
        ----------
        session : requests.sessions.Session
            HTTP session object. None by default
        path : str
            Endpoint path, e.g. profile/user. Empty string by default
        query_params : dict or str or list of tuples
            Query params, e.g. {'param': 'value'}, 'param=value', (param, value).
            None by default
        headers : dict
            Request headers, e.g. {'key': 'value'}. None by default
        request_body : dict
            Request body, e.g. {'key': 'value'}. None by default

        Returns
        -------
        response : requests.models.Response
            Response returned by DELETE request
        """
        self._log_request_body_params_headers(query_params, headers, request_body)
        if session:
            return session.delete(url=urljoin(self.host, path),
                                  params=query_params,
                                  headers=headers,
                                  json=request_body,
                                  verify=False)
        return requests.delete(url=urljoin(self.host, path),
                               params=query_params,
                               headers=headers,
                               json=request_body,
                               verify=False)

    def _log_request_body_and_headers(self, body, headers):
        self.logger.debug(LOG_SEPARATOR)
        self.logger.debug('REQUEST BODY: %s', body)
        self.logger.debug('\nREQUEST HEADERS: %s', headers)

    def _log_request_params_and_headers(self, params, headers):
        self.logger.debug(LOG_SEPARATOR)
        self.logger.debug('QUERY PARAMS: %s', params)
        self.logger.debug('\nREQUEST HEADERS: %s', headers)

    def _log_request_body_params_headers(self, params, headers, body):
        self.logger.debug(LOG_SEPARATOR)
        self.logger.debug('QUERY PARAMS: %s', params)
        self.logger.debug('\nREQUEST HEADERS: %s', headers)
        self.logger.debug('REQUEST BODY: %s', body)
