from utils.helper_funcs import (
    get_value_by_json_path,
    file_content
)


class ResponseHandler:
    """
    Processes HTTP response.

    Parameters
    ----------
    resp : requests.models.Response
        Response object

    Attributes
    ----------
    resp : requests.models.Response
        Response object
    """

    def __init__(self, resp):
        self.resp = resp

    def get_status_code(self):
        """
        Returns status code of HTTP request.

        Returns
        -------
        status_code : int
            HTTP status code
        """
        return self.resp.status_code

    def get_response_headers(self):
        """
        Returns response headers.

        Returns
        -------
        headers : dict
            CaseInsensitiveDict of response headers
        """
        return self.resp.headers

    def get_json(self):
        """
        Returns json-encoded content of response.

        Returns
        -------
        resp in json format : dict
            Json-encoded content of response
        """
        return self.resp.json()

    def get_content(self):
        """
        Returns response content in bytes.

        Returns
        -------
        content : bytes
            Response content
        """
        return self.resp.content

    def get_response_header(self, header_name):
        """
        Returns response header value.

        Parameters
        ----------
        header_name : str
            Response header name

        Returns
        -------
        header value : str
            Response header value
        """
        return self.resp.headers[header_name]

    def get_json_key_value(self, json_path):
        """
        Returns JSON key value by provided json path.

        Parameters
        ----------
        json_path : str
            Path to JSON key

        Returns
        -------
        key value : str
            JSON key value
        """
        return get_value_by_json_path(self.resp.json(), json_path)

    def response_equals(self, expected_response):
        """
        Compares actual plain text response with expected response from file.

        Parameters
        ----------
        expected_response : str
            Relative path to file with expected content

        Returns
        -------
        true or false : bool
            If actual_response has the same content as expected_response
        """
        expected_response = file_content(expected_response)
        return self.resp.text == expected_response

    def get_text(self):
        """
        Get response as unicode text.

        Returns
        -------
        response text : str
            Response text
        """
        return self.resp.text
