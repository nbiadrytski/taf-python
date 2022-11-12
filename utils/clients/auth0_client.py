from os import environ
from urllib.parse import urljoin

from utils.constants import AUTH0_TOKEN_PATH

from utils.http_utils import ApiClient
from utils.helper_funcs import replace_chars_if_needed
from utils.data_enums import (
    Auth0Keys,
    Envs,
    EnvVars
)


class Auth0Client(ApiClient):
    """
    Auth0 actions.

    Parameters
    ----------
    env_params : function
        Returns app2, DRAP and Auth0 hosts. Overrides env_params from super ApiClient
    session : function
        Returns <requests.sessions.Session> object. Overrides session from super ApiClient

    Attributes
    ----------
    auth0_api_v2_token : str
        Auth0 api/v2 bearer token to search/delete auth0 users
    """

    def __init__(self, env_params, session=None):
        super().__init__(env_params, session)

        if Envs.AUTH0_DEV.value == env_params[2]:
            self.auth0_api_v2_token = self.create_auth0_api_v2_token(
                auth0_client_id=environ[EnvVars.AUTH0_DEV_CLIENT_ID.value],
                auth0_client_secret=environ[EnvVars.AUTH0_DEV_CLIENT_SECRET.value]
            )
        else:
            self.auth0_api_v2_token = self.create_auth0_api_v2_token(
                auth0_client_id=environ[EnvVars.AUTH0_PROD_CLIENT_ID.value],
                auth0_client_secret=environ[EnvVars.AUTH0_PROD_CLIENT_SECRET.value]
            )

    def create_auth0_api_v2_token(self, auth0_client_id, auth0_client_secret):

        payload = {'grant_type': 'client_credentials',
                   'audience': urljoin(self.auth0_host, 'api/v2/'),
                   'client_id': auth0_client_id,
                   'client_secret': auth0_client_secret}

        resp = self.auth0_post_request(AUTH0_TOKEN_PATH, payload)
        self.auth0_api_v2_token = self.get_value_from_json_response(
            resp, Auth0Keys.ACCESS_TOKEN.value)

        self.logger.info('Generated Auth api/v2 token: %s',
                         self.auth0_api_v2_token)

        return self.auth0_api_v2_token

    def get_auth0_user_id_by_username(self, username):

        resp = self.auth0_get_request(
            'api/v2/users-by-email',
            query_params=f'email={replace_chars_if_needed(username)}')
        auth0_user_id = self.get_value_from_json_response(
            resp, Auth0Keys.USER_ID.value)

        self.logger.info('Found auth0 user %s. User id: %s', username, auth0_user_id)

        return auth0_user_id

    def get_auth0_portal_id_by_username(self, username):

        resp = self.auth0_get_request(
            'api/v2/users-by-email',
            query_params=f'email={replace_chars_if_needed(username)}')
        portal_id = self.get_value_from_json_response(resp,
                                                      Auth0Keys.PORTAL_ID.value)
        self.logger.info('Found portal_id %s for auth0 user %s',
                         portal_id, username)

        return portal_id

    def delete_auth0_user(self, username):

        user_id = self.get_auth0_user_id_by_username(username)

        resp = self.auth0_delete_request(f'api/v2/users/{user_id}',
                                         check_status_code=False)
        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'Auth0 user {username} with id {user_id} was not deleted')

        self.logger.info('Deleted auth0 user: %s', username)
