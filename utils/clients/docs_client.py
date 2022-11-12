from utils.http_utils import ApiClient


class DocsPortalClient(ApiClient):
    """
    Docs Portal actions.

    Parameters
    ----------
    env_params : function
        Returns app2, DRAP and Auth0 hosts.
        Overrides env_params from super ApiClient
    session : function
        Returns <requests.sessions.Session> object.
        Overrides session from super ApiClient
    """

    def __init__(self, env_params, session=None):
        super().__init__(env_params, session)

    def search(self, query, page=0, filters=None):
        """
        Docs Portal GET /search

        Parameters
        ----------
        query : str
            Query param string
        page : int
            Current page
        filters : str
            Filter search by: itemType:platform, itemType:api,
            itemType:tutorials

        Returns
        -------
        resp : Response
            Response object
        """
        path = 'search'
        params = f'query={query}&page={page}'
        if filters:
            params = f'query={query}&page={page}&filters={filters}'

        resp = self.docs_get_request('search', params)

        self.logger.info('Called Get /%s?%s endpoint', path, params)

        return resp
