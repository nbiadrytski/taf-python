from urllib.parse import urlparse
from ntpath import basename
from time import time
from datetime import date

from time import sleep

from utils.helper_funcs import (
    update_rfc3339_date,
    sign_up_payload,
    time_left,
    get_substring_by_pattern,
    replace_chars_if_needed
)
from utils.constants import (
    API_V2_PATH,
    USER_PASSWORD,
    CONTACT_US,
    API_V2_DEPLOYMENTS_PATH,
    API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
    OFFICE_DOCUMENT_RESPONSE_HEADER,
    DR_DEV_ORG_ID_STAGING,
    DR_DEV_ORG_ID_PROD,
    TEN_K_DIABETES_DATASET,
    TEN_K_DIABETES_TARGET,
    EUCLIDIAN_DISTANCE_MODEL,
    TIMEOUT_MESSAGE,
    PAYG_FLAGS,
    TRIAL_FLAGS,
    CREATE_INVOICE_PATH,
    WHAT_IF_APP_ID
)
from utils.http_utils import ApiClient
from utils.data_enums import (
    PredictionServersKeys,
    PostApiV2UsersKeys,
    PostJoinKeys,
    ProjectKeys,
    ApiV2ApiKeys,
    DatasetUploadKeys,
    ProjectStatusKeys,
    ModelsKeys,
    FromLearningModelKeys,
    FromRecommendedModelKeys,
    DeploymentsKeys,
    AppsKeys,
    ModelValidationKeys,
    AccountLoginKeys,
    RecommendedModelsKeys,
    CommentsKeys,
    DatasetsDatasetIdKeys,
    BalanceSummaryKeys,
    NfKeys,
    UserType,
    ModelingMode
)
from utils.data_enums import FeatureFlags


COMPLETED_STATUS = 'COMPLETED'


class AppClient(ApiClient):
    """
    Performs user actions using v2, internal or DataRobot client API.

    Parameters
    ----------
    env_params : function
        Returns a tuple of  app host and admin's API key.
        Overrides env_params from super ApiClient
    session : function
        Returns <requests.sessions.Session> object. None by default.
        Overrides session from super ApiClient

    Attributes
    ----------
    user_id : str
        User id is initialised here. None by default
    project_id : str
        User's project id is initialised here. None by default
    """

    def __init__(self, env_params, session=None):
        super().__init__(env_params, session)
        self.user_id = None
        self.project_id = None

    def v2_create_user_request(self, payload):
        """
        Calls POST api/v2/users/ and stores response.

        Parameters
        ----------
        payload : dict
            Request body for user creation request

        Returns
        -------
        response : requests.models.Response
            Response
        """
        return self.v2_api_admin_post_request(f'{API_V2_PATH}/users/', payload)

    def create_trial_user(self,
                          username,
                          first_name,
                          last_name,
                          days_to_expire=14,
                          ahead=True,
                          enable_agreement=False,
                          link_dr_account=False):
        """
        Creates TrialUser.
        Returns inviteLink to sign up the user.

        Parameters
        ----------
        username : str
            Username in name@domain.com format
        first_name : str
            User's first name
        last_name : str
            User's last name
        days_to_expire : int
            N days for PAYG user to expire. 14 by default
        ahead : bool
            Set expiration date ahead (True) or back (False) by N of days.
        enable_agreement : bool
            If requireClickthroughAgreement or not.
        link_dr_account : bool
            If to create Auth0 account or not

        Returns
        -------
        invite_link : str
            User can sign up by following the invite link
        """
        payload = {'userType': UserType.TRIAL_USER.value,
                   'username': username,
                   'firstName': first_name,
                   'lastName': last_name,
                   'expirationDate': update_rfc3339_date(
                       days=days_to_expire, ahead=ahead),
                   'requireClickthroughAgreement': enable_agreement,
                   'drAccountOptions': {'link': link_dr_account},
                   'permissionsDiff': TRIAL_FLAGS}

        resp = self.v2_create_user_request(payload)
        invite_link = self.get_value_from_json_response(
            resp, PostApiV2UsersKeys.INVITE_LINK.value)

        self.logger.info('TrialUser was created. Invite link: %s',
                         invite_link)
        return invite_link

    def create_payg_user(self,
                         username,
                         first_name,
                         last_name,
                         country='US',
                         enable_agreement=False,
                         create_drap_user=False,
                         initial_credits=10,
                         link_dr_account=False):
        """
        Creates PayAsYouGoUser.
        Optionally creates DataRobot Portal Account.
        Returns inviteLink to sign up the user.

        Parameters
        ----------
        username : str
            Username in name@domain.com format
        first_name : str
            User's first name
        last_name : str
            User's last name
        country : str
            User's country, e.g. US
        enable_agreement : bool
            If requireClickthroughAgreement (Terms & Conditions) or not.
        create_drap_user : bool
            If to create DataRobot Portal Account or not
        initial_credits : int
            Amount of initials credits to grant
        link_dr_account : bool
            If to create Auth0 account or not

        Returns
        -------
        invite_link : str
            User can sign up by following the invite link
        """
        dr_account_options = {
            'link': link_dr_account,
            'createDrPortalAccount': create_drap_user
        }
        if create_drap_user:
            dr_account_options = {'link': link_dr_account,
                                  'createDrPortalAccount': create_drap_user,
                                  'creditsGrant': initial_credits}
        payload = {'userType': UserType.PAYG_USER.value,
                   'username': username,
                   'firstName': first_name,
                   'lastName': last_name,
                   'country': country,
                   'requireClickthroughAgreement': enable_agreement,
                   'drAccountOptions': dr_account_options,
                   'permissionsDiff': PAYG_FLAGS}

        resp = self.v2_create_user_request(payload)
        invite_link = self.get_value_from_json_response(
            resp, PostApiV2UsersKeys.INVITE_LINK.value)

        self.logger.info('PayAsYouGoUser was created. Invite link: %s',
                         invite_link)
        return invite_link

    def setup_self_service_user(self, username, first_name, last_name,
                                user_type=UserType.PAYG_USER.value,
                                link_dr_account=False):
        """
        1. Creates PayAsYouGoUser or TrialUser
        2. Signs up the user
        3. Creates API key for the user
        Returns user ID.

        Parameters
        ----------
        username : str
            User's email
        first_name : str
            User's first name
        last_name : str
            User's last name
        user_type : str
            Either PayAsYouGoUser or TrialUser
        link_dr_account : bool
            If to create Auth0 account or not

        Returns
        -------
        user_id : str
            User ID
        """
        if user_type == UserType.TRIAL_USER.value:
            invite_link = self.create_trial_user(username,
                                                 first_name,
                                                 last_name,
                                                 link_dr_account=link_dr_account)
        else:
            invite_link = self.create_payg_user(username,
                                                first_name,
                                                last_name,
                                                link_dr_account=link_dr_account)
        self.open_invite_link(invite_link)
        user_id = self.sign_up_payg_user(first_name, last_name)

        self.v2_create_api_key()

        return user_id

    def create_user(self,
                    username,
                    first_name,
                    last_name,
                    user_type=UserType.PRO_USER.value,
                    enable_agreement=False,
                    language='en',
                    second_user=False,
                    add_permissions=False,
                    new_permissions=None):
        """
        Creates a user with POST api/v2/users/.

        Parameters
        ----------
        username : str
            Username in name@domain.com format
        first_name : str
            User's first name
        last_name : str
            User's last name
        user_type : str
            'ProUser' by default
        enable_agreement : bool
            If requireClickthroughAgreement (DataRobot Terms & Conditions) or not.
            False by default
        language : str
            English by default
        second_user : bool
            Create a second user for the test or not
        add_permissions : bool
            If to add permissions to the existing dict or not
        new_permissions : dict
            Dict od additional user permissions

        Returns
        -------
        user_id : str
            User id
        """
        org_id = DR_DEV_ORG_ID_STAGING
        if self.app_host == 'prod':
            org_id = DR_DEV_ORG_ID_PROD

        permissions = {
            FeatureFlags.EXPERIMENTAL_API_ACCESS.value: True
        }
        if add_permissions:
            permissions.update(new_permissions)

        payload = {
            'userType': user_type,
            'organizationId': org_id,
            'username': username,
            'firstName': first_name,
            'lastName': last_name,
            'password': USER_PASSWORD,
            'requireClickthroughAgreement': enable_agreement,
            'language': language,
            'permissionsDiff': permissions
        }
        if user_type == UserType.BASIC_USER.value:
            # organizationId is not needed for BasicUser
            del payload['organizationId']
            payload.update(
                {'expirationDate': update_rfc3339_date(
                    days=14, ahead=True)})

        resp = self.v2_create_user_request(payload)

        if second_user:
            user_id = self.get_value_from_json_response(
                resp,
                PostApiV2UsersKeys.USER_ID.value
            )
            self.logger.info(
                'Second %s was created. User Id: %s',
                user_type, user_id
            )
            return user_id

        self.user_id = self.get_value_from_json_response(
            resp,
            PostApiV2UsersKeys.USER_ID.value
        )
        self.logger.info(
            '%s was created. User Id: %s',
            user_type, self.user_id
        )
        return self.user_id

    def login(self, username, password=USER_PASSWORD):
        """
        Logs user in POST /account/login.

        Parameters
        ----------
        username : str
            Username in name@domain.com format,
            e.g. staging.test.user+self_service_api_tests_9666886467@datarobot.com
        password : str
            User password (Testing123 by default)
        """
        payload = {'username': username,
                   'password': password}

        self.get_value_from_json_response(
            self.internal_api_post_request('/account/login', payload),
            AccountLoginKeys.UID.value)

        self.logger.info('User %s logged in', username)

    def logout(self):
        """Logs user out GET /account/logout."""

        self.internal_api_get_request('/account/logout')

        self.logger.info('User %s logged out', self.user_id)

    def account_profile(self):
        """
        GET /account/profile.

        Returns
        -------
        resp : Response
            Response object
        """
        resp = self.internal_api_get_request('/account/profile')

        self.logger.info('GET /account/profile was called for user %s', self.user_id)

        return resp

    def post_account_profile(self, payload, check_status_code=True):
        """
        Updates user profile POST /account/profile.
        E.g. turn on 'Enable email notification when Autopilot has finished' switcher

        Parameters
        ----------
        payload : dict
            Request payload
        check_status_code : bool
            If to check status code is 200 or not

        Returns
        -------
        resp : Response
            Response object
        """
        resp = self.internal_api_post_request(
            '/account/profile', payload, check_status_code=check_status_code)

        self.logger.info('Updated user %s profile: %s', self.user_id, payload)

        return resp

    def open_invite_link(self, invite_link):
        """
        Calls invite_link returned by create_payg_user().
        This step is required to sign up a user.

        Parameters
        ----------
        invite_link : str
            Invite link url for user to sign up
        """
        self.internal_api_get_request(
            urlparse(invite_link).path, urlparse(invite_link).query)

        self.logger.info('Invite link %s was opened', invite_link)

    def sign_up_payg_user(self, first_name, last_name):
        """
        Signs up PayAsYouGoUser by POST /join.

        Parameters
        ----------
        first_name : str
            User's first name
        last_name : str
            User's last name

        Returns
        -------
        user_id : str
            Used in app_client fixture for PayAsYouGoUser set up and teardown
        """
        payload = sign_up_payload(first_name, last_name)

        self.user_id = self.get_value_from_json_response(
            self.internal_api_post_request('/join', payload),
            PostJoinKeys.USER_ID.value)

        self.logger.info('User %s signed up', self.user_id)

        return self.user_id

    def v2_create_api_key(self):
        """
        Creates user's API key POST api/v2/account/apiKeys/.

        Returns
        -------
        api_key : str
            User's API key
        """
        payload = {'name': 'nice_api_key'}

        resp = self.app_request.post_request(session=self.http_session,
                                             path=f'{API_V2_PATH}/account/apiKeys/',
                                             request_body=payload)
        self.assert_status_code(resp,
                                expected_code=201,
                                actual_code=self.status_code(resp),
                                message='API key was not created')

        self.user_api_key = self.get_value_from_json_response(resp,
                                                              ApiV2ApiKeys.KEY.value)

        self.logger.info('API key %s was created', self.user_api_key)

        return self.user_api_key

    def v2_update_user_expiration_date(self, days, userid=None, ahead=True):
        """
        Updates user's expirationDate PATCH api/v2/users/{user_id}/.

        Parameters
        ----------
        days : int
            N of days for expirationDate to be updated
        userid : str
            User id. None by default
        ahead : bool
            Set expirationDate ahead (True) or back (False) by N of days
        """
        expiration_date = update_rfc3339_date(days=days, ahead=ahead)
        payload = {'expirationDate': expiration_date}
        # self.user_id is a unique user per test
        # created and then deleted in app_client (set up / tear down) fixture
        if userid is None:
            user_id = self.user_id
        else:
            # other user's user_id can be passed as well
            user_id = userid
        resp = self.v2_api_admin_patch_request(f'{API_V2_PATH}/users/{user_id}/',
                                               payload,
                                               check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=204,
                                actual_code=self.status_code(resp),
                                message=f'User\'s {user_id} expiration date was not updated')

        self.logger.info('User\'s %s expirationDate is now: %s', user_id, expiration_date)

    def v2_create_project_from_file(self, file_path, poll_interval=3, timeout_period=10):
        """
        Creates a project from a local file POST api/v2/projects.
        Polls for GET api/v2/status/{id} until the project is created.
        Returns project_id from GET api/v2/projects/{pid}/.

        Parameters
        ----------
        file_path : str
            Path to data/datasets/file.extension
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now

        Returns
        -------
        project_id : str
            Project id
        """
        with open(file_path, 'rb') as upload_file:
            dataset_name = basename(file_path)
            payload = {'file': (dataset_name, upload_file)}

            create_project_resp = self.v2_api_post_request(f'{API_V2_PATH}/projects/',
                                                           files=payload,
                                                           check_status_code=False)
            self.logger.info(
                'Trying to start project creation for %s dataset', dataset_name)

        self.assert_status_code(create_project_resp,
                                expected_code=202,
                                actual_code=self.status_code(create_project_resp),
                                message='Project creation was not started')

        project_status_url = self.get_location_header(create_project_resp)

        timeout = time() + 60 * timeout_period
        while True:
            # poll GET api/v2/status/{id} till redirected to GET api/v2/projects/{pid}/
            # allow_redirects=False to get Location response header
            project_status_resp = self.v2_api_get_request(urlparse(project_status_url).path,
                                                          allow_redirects=False,
                                                          check_status_code=False)
            self.logger.info('Project is being created: %s. Will stop polling in: %s',
                             project_status_url, time_left(timeout))

            if time() > timeout:
                self.logger.error('Timed out creating project %s after %d minutes',
                                  project_status_url, timeout_period)
                raise TimeoutError(
                    f'Timed out creating project {project_status_url} after {timeout_period} minutes')

            if self.status_code(project_status_resp) == 303:
                project_url = self.get_location_header(project_status_resp)
                self.project_id = project_url.split('/')[6]
                break

            sleep(poll_interval)

        self.logger.info('Project %s was created.', self.project_id)

        return self.project_id

    def setup_10k_diabetes_project(self):
        """
        Sets up 10k_diabetes project:
        1. Creates a project
        2. Sets a target
        3. Start modeling in manual mode
        4. Waits until EDA is done
        5. Trains a model
        6. Deploys the model

        Returns
        -------
        project_id, bp_id, model_id, deployment_id : tuple
            Returns project_id, bp_id, model_id, deployment_id
        """
        project_id = self.v2_create_project_from_file(TEN_K_DIABETES_DATASET)
        self.set_target(TEN_K_DIABETES_TARGET, project_id)
        self.v2_start_autopilot(project_id, TEN_K_DIABETES_TARGET, ModelingMode.MANUAL.value)
        self.poll_for_eda_done(project_id, 17)

        # Get blueprint id for
        # Auto-tuned K-Nearest Neighbors Classifier (Euclidean Distance) model
        bp_id = self.v2_get_blueprint_id(EUCLIDIAN_DISTANCE_MODEL, project_id)
        model_id = self.v2_train_model(project_id, bp_id)
        deployment_id = self.v2_deploy_from_learning_model(model_id)

        return project_id, bp_id, model_id, deployment_id

    def v2_delete_project(self):
        """Deletes user-created project DELETE api/v2/projects/{pid}."""

        resp = self.v2_api_delete_request(f'{API_V2_PATH}/projects/{self.project_id}/',
                                          check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=204,
                                actual_code=self.status_code(resp),
                                message=f'Project {self.project_id} was not deleted')

        self.logger.info('Project %s was deleted', self.project_id)

    def v2_delete_project_by_project_id(self, project_id):
        """
        Deletes a project DELETE api/v2/projects/{pid} by project_id.

        Parameters
        ----------
        project_id : str, int
            Project id
        """
        resp = self.v2_api_delete_request(f'{API_V2_PATH}/projects/{project_id}/',
                                          check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=204,
                                actual_code=self.status_code(resp),
                                message=f'Project {project_id} was not deleted')

        self.logger.info('Project %s was deleted', project_id)

    def v2_delete_payg_user(self, userid):
        """
        Deletes PayAsYouGoUser DELETE api/v2/users/{user_id}.
        Also used as a tear down method in app_client fixture.

        Parameters
        ----------
        userid : str
            User id to be deleted
        """
        if userid is None:
            # self.user_id is a unique user per test
            # created and then deleted in app_client (set up / tear down) fixture
            user_id = self.user_id
        else:
            # other user's user_id can be passed as well
            user_id = userid
        resp = self.v2_api_admin_delete_request(f'{API_V2_PATH}/users/{user_id}/',
                                                check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'User {user_id} was not deleted')

        self.logger.info('User %s was deleted', user_id)

    def create_project_without_dataset(self):
        """
        Creates Untitled Project (without uploading a dataset) POST /project.

        Returns
        -------
        project_id : str
            Project id
        """
        self.project_id = self.get_value_from_json_response(
            self.internal_api_post_request('/project'), ProjectKeys.ID.value)

        self.logger.info('Project %s was created', self.project_id)

        return self.project_id

    def upload_dataset(self, file_path, project_id):
        """
        Uploads dataset from a local file POST /upload/{pid}.

        Parameters
        ----------
        file_path : str
            Path to data/datasets/dataset_file.extension
        project_id : str
            Project id
        """
        with open(file_path, 'rb') as upload_file:
            dataset_name = basename(file_path)
            payload = {'file': (dataset_name, upload_file)}

            resp = self.internal_api_post_request('/upload/{}'.format(project_id),
                                                  files=payload)
        is_dataset_uploaded = self.get_value_from_json_response(
            resp, DatasetUploadKeys.UPLOAD_SUCCESS.value)

        assert is_dataset_uploaded == '1', \
            f'Dataset "{dataset_name}" was not uploaded. ' \
            f'Status code: {self.status_code(resp)}. ' \
            f'Response: {self.get_response_text(resp)}'

        self.logger.info('Dataset %s was uploaded for project %s',
                         dataset_name, project_id)

    def poll_for_eda_done(self, project_id, eda_status, poll_interval=3, timeout_period=15):
        """
        Polls for GET /project/{pid}/status to return specified status.
        Status 9 -- pre start EDA is finished.
        Status 17 -- post start EDA is finished.

        Parameters
        ----------
        project_id : str, int
            Project id
        eda_status : int
            Status of EDA process
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now
        """
        timeout = time() + 60 * timeout_period
        while True:
            status = self.get_value_from_json_response(
                self.internal_api_get_request(f'/project/{project_id}/status',
                                              check_status_code=False),
                ProjectStatusKeys.EDA_STATUS.value)

            self.logger.info('Polling for EDA status %d for project %s. Status: %d. '
                             'Will stop polling in %s',
                             eda_status, project_id, status, time_left(timeout))

            if time() > timeout:
                self.logger.error('Timed out polling for EDA status %d for project %s '
                                  'after %d minutes', eda_status, project_id, timeout_period)
                raise TimeoutError(f'Timed out polling for EDA status {eda_status} '
                                   f'after {timeout_period} minutes')

            if status == eda_status:

                self.logger.info('EDA is completed for project %s. Status: %d',
                                 project_id, status)
                break
            sleep(poll_interval)

    def set_target(self, target, project_id):
        """
        Sets project's target GET eda/profile/{pid}/{target}.

        Parameters
        ----------
        target : str
            Name of the target feature
        project_id : str or int
            Project id
        """
        self.internal_api_get_request(f'/eda/profile/{project_id}/{target}')

        self.logger.info('Target "%s" is set for project %s', target, project_id)

    def get_project_queue_settings(self, project_id):
        """
        Gets project's queue settings.
        GET project/{pid}/queue/settings.

        Parameters
        ----------
        project_id : str or int
            Project id

        Returns
        -------
        resp : Response
            Response object
        """
        resp = self.internal_api_get_request(f'/project/{project_id}/queue/settings')

        self.logger.info('Called GET project/%s/queue/settings endpoint', project_id)

        return resp

    def train_models(self, project_id, blueprints):
        """
        Starts to train models based on the passed list of blueprints dicts.
        POST project/{project_id}/models.

        Parameters
        ----------
        project_id : str
            Project ID
        blueprints : list
            List of blueprints dicts
        """
        resp = self.internal_api_post_request(f'project/{project_id}/models', blueprints)

        self.logger.info('Started to train models %s for project %s: %s',
                         blueprints, project_id, self.get_response_json(resp)['message'])

    def v2_get_blueprint_id(self, blueprint_name, project_id):
        """
        Returns blueprint_id by passed blueprint_name.
        If there was no exact match,
        Returns next available blueprint_id
        If next modelType contains that blueprint_name.

        Parameters
        ----------
        blueprint_name : str
            Blueprint's modelType value
        project_id : str, int
            Project id

        Returns
        -------
        blueprint_id : str
            Blueprint id (Repository tab)
        """
        blueprints = self.get_response_json(
            self.v2_api_get_request(f'{API_V2_PATH}/projects/{project_id}/blueprints/'))

        # find a blueprint dict from the list of blueprints
        # where blueprint_name is exactly modelType value
        exact_match = [bp for bp in blueprints
                       if bp['modelType'] == blueprint_name]
        if exact_match:
            blueprint_id = exact_match[0]['id']
            self.logger.info('Found a blueprint match: %s', blueprint_id)
            return blueprint_id
        # find a blueprint dict from the list of blueprints
        # where modelType value contains blueprint_name string
        blueprint_id = next(
            bp for bp in blueprints if blueprint_name in bp['modelType'])

        self.logger.info('Found next available blueprint %s', blueprint_id)

        return blueprint_id

    def v2_train_model(self, project_id, blueprint_id, poll_interval=3, timeout_period=25):
        """
        Starts model training process for blueprint POST api/v2/projects/{pid}/models/.
        Polls GET api/v2/projects/{pid}/modelJobs/{model_job_id}/ until 303 is returned.
        Then redirects to GET api/v2/{pid}/models/{model_id} to get model id.

        Parameters
        ----------
        project_id : str, int
            Project id
        blueprint_id : str
            Blueprint id
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes

        Returns
        -------
        model_id : str
            Model id
        """
        payload = {'blueprintId': blueprint_id}

        model_resp = self.v2_api_post_request(f'{API_V2_PATH}/projects/{project_id}/models/',
                                              payload,
                                              check_status_code=False)
        self.logger.info(
            'Trying to start model creation for blueprint %s', blueprint_id)

        self.assert_status_code(model_resp,
                                expected_code=202,
                                actual_code=self.status_code(model_resp),
                                message=f'Model creation for blueprint {blueprint_id}'
                                        f' was not started')
        model_job_url = self.get_location_header(model_resp)

        timeout = time() + 60 * timeout_period
        while True:
            model_job_resp = self.v2_api_get_request(urlparse(model_job_url).path,
                                                     allow_redirects=False,
                                                     check_status_code=False)
            self.logger.info('Model is being created: %s. Will stop polling in %s',
                             model_job_url, time_left(timeout))

            if time() > timeout:
                self.logger.error('Timed out training model %s after %d minutes',
                                  model_job_url, timeout_period)
                raise TimeoutError(
                    f'Timed out training model {model_job_url} after {timeout_period} minutes')

            if self.status_code(model_job_resp) == 303:
                model_url = self.get_location_header(model_job_resp)
                model_id = self.get_value_from_json_response(
                    self.v2_api_get_request(urlparse(model_url).path), ModelsKeys.ID.value)
                break

            sleep(poll_interval)

        self.logger.info('Model %s was created.', model_id)

        return model_id

    def v2_start_autopilot(self,
                           project_id,
                           target,
                           mode,
                           datetime_partition_column=None,  # e.g. Date
                           multiseries_id_columns=None,  # [Column name]
                           windows_basis_unit=None,  # e.g. DAY
                           cv_method=None,
                           blend_best_models=True,
                           time_series=False):
        """
        Start modelling process with PATCH api/v2/projects/{project_id}/aim/

        Parameters
        ----------
        project_id : str, int
            Project id
        target : str
            Name of the target feature
        mode : str
            Autopilot mode: auto, quick, manual
        datetime_partition_column : str
            Date column that will be used as a datetime partition column
        multiseries_id_columns : list
            Names of columns identifying the series to which each row of the dataset belongs
        windows_basis_unit : str
            Indicates which unit is basis for feature derivation window and forecast window
        cv_method : str
            Partitioning method: random, stratified, datetime, user, group
        blend_best_models : bool
            If to create blender models or not
        time_series : bool
            Run Autopilot for time series project or not
        """
        payload = {'target': target,
                   'mode': mode,
                   'blendBestModels': blend_best_models}
        if time_series:
            payload.update({'cvMethod': cv_method,
                            'datetimePartitionColumn': datetime_partition_column,
                            'useTimeSeries': True,
                            'windowsBasisUnit': windows_basis_unit})
        if multiseries_id_columns is not None:
            payload.update({'multiseriesIdColumns': multiseries_id_columns})

        resp = self.v2_api_patch_request(f'{API_V2_PATH}/projects/{project_id}/aim/',
                                         payload,
                                         check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Autopilot WAS NOT started for project {project_id}')

        self.logger.info('Autopilot with target "%s" in "%s" mode started for project %s',
                         target, mode, project_id)

    def v2_get_prediction_server_id(self):
        """
        Returns prediction server id
        if GET api/v2/predictionServers returns any servers.
        Otherwise, returns empty string.

        Returns
        -------
        prediction_server_id: str
            Prediction server id or empty string if no server returned
        """
        resp = self.v2_api_get_request(f'{API_V2_PATH}/predictionServers')

        if self.get_value_from_json_response(
                resp, PredictionServersKeys.COUNT.value) != 0:
            server_id = self.get_value_from_json_response(
                resp,
                PredictionServersKeys.SERVER_ID.value)
            self.logger.info('Prediction server id: %s',
                             server_id)
            return server_id

        return ''

    def v2_get_prediction_endpoint(self):
        """
        Returns prediction endpoint, e.g. https://payasyougo.dynamic.orm.datarobot.com.
        GET api/v2/predictionServers endpoint.

        Returns
        -------
        prediction_endpoint : str
            Prediction endpoint host
        """
        prediction_endpoint = self.get_value_from_json_response(
            self.v2_api_get_request(f'{API_V2_PATH}/predictionServers'),
            PredictionServersKeys.ENDPOINT.value)

        self.logger.info('Prediction endpoint: %s', prediction_endpoint)

        return prediction_endpoint

    def v2_get_datarobot_key(self):
        """
        Returns DataRobot key, e.g. 2e0f8d05-c6a8-5ec7-7e99-353c23635dc1.
        GET api/v2/predictionServers endpoint.

        Returns
        -------
        datarobot_key : str
            DataRobot key
        """
        datarobot_key = self.get_value_from_json_response(
            self.v2_api_get_request(f'{API_V2_PATH}/predictionServers'),
            PredictionServersKeys.DATAROBOT_KEY.value)

        self.logger.info('Datarobot key: %s', datarobot_key)

        return datarobot_key

    def v2_deploy_from_learning_model(self, model_id):
        """
        Deploys a model from Models Leaderboard.
        POST api/v2/deployments/fromLearningModel/.

        Parameters
        ----------
        model_id : str
            Model id

        Returns
        -------
        deployment_id : str
            Deployment id
        """
        payload = {'modelId': model_id,
                   'label': f'deployment_for_{model_id}'}

        deployment_id = self.get_value_from_json_response(
            self.v2_api_post_request(f'{API_V2_DEPLOYMENTS_PATH}/fromLearningModel/',
                                     payload),
            FromLearningModelKeys.DEPLOYMENT_ID.value)

        self.logger.info('Model %s has been deployed. '
                         'Deployment id: %s', model_id, deployment_id)

        return deployment_id

    def v2_is_model_valid_for_replacement(self, model_id, deployment_id):
        """
        Deploys a model from Models Leaderboard.
        POST api/v2/deployments/fromLearningModel/.

        Parameters
        ----------
        model_id : str
            Model ID
        deployment_id : str
            Deployment ID

        Returns
        -------
        is model valid for replacement : bool
            If model is valid to replace a model from deployment
        """
        payload = {'modelId': model_id}

        resp = self.v2_api_post_request(
            f'{API_V2_DEPLOYMENTS_PATH}/{deployment_id}/model/validation/', payload)

        if self.get_value_from_json_response(resp, ModelValidationKeys.MESSAGE.value) == \
               'Model can be used to replace the current model of the deployment.':

            self.logger.info('Deployment %s model can be replaced with model %s',
                             deployment_id, model_id)
            return True

        self.logger.error('Deployment %s model cannot be replaced with model %s. '
                          'Response: %s',
                          deployment_id, model_id, self.get_response_text(resp))
        return False

    def v2_get_model_jobs(self, project_id):
        """
        Get model jobs: status, processes, modelType, etc.
        GET api/v2/projects/{project_id}/modelJobs/.

        Parameters
        ----------
        project_id : str
            Project ID

        Returns
        -------
        resp : Response
            Response object with a list of jobs (or empty list)
        """
        resp = self.v2_api_get_request(
            f'{API_V2_PATH}/projects/{project_id}/modelJobs/')

        self.logger.info('GET %s/projects/%s/modelJobs/ was called. '
                          '%d jobs are running',
                          API_V2_PATH, project_id, len(self.get_response_json(resp)))
        return resp

    def v2_get_model_id_by_name(self, project_id, model_name):
        models = self.get_response_json(
            self.v2_api_get_request(f'{API_V2_PATH}/projects/{project_id}/models/'))

        # find a model dict from the list of models
        # where model_name is exact modelType value
        exact_match = [model for model in models
                       if model['modelType'] == model_name]
        if exact_match:
            model_id = exact_match[0]['id']

            self.logger.info('Found a model %s match: %s', model_name, model_id)

            return model_id
        # find a model dict from the list of models
        # where modelType value contains model_name string
        model_id = next(
            model for model in models if model_name in model[ModelsKeys.TYPE.value])

        self.logger.info('Found next available model %s', model_id)

        return model_id

    def v2_replace_deployment_model(self,
                                    deployment_id,
                                    model_id,
                                    reason='DATA_DRIFT',
                                    poll_interval=1,
                                    timeout_period=25):
        """
        Replaces deployed model with another model.
        POST api/v2/deployments/{deployment_id}/model/.
        Valid reasons: ACCURACY, DATA_DRIFT, ERRORS, SCHEDULED_REFRESH, SCORING_SPEED, OTHER

        Parameters
        ----------
        model_id : str
            Model ID
        deployment_id : str
            Deployment ID
        reason : str
            Replacement reason
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes
        """
        payload = {'modelId': model_id,
                   'reason': reason}

        resp = self.v2_api_patch_request(f'{API_V2_DEPLOYMENTS_PATH}/{deployment_id}/model/',
                                         payload,
                                         check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Deployment {deployment_id} model was not replaced '
                                        f'by model {model_id} with reason {reason}')

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(urlparse(self.get_location_header(resp)).path,
                                                  allow_redirects=False,
                                                  check_status_code=False)
            self.logger.info('Waiting for deployment %s model to be replaced by %s model. '
                             'Will stop polling in %s', deployment_id, model_id, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out replacing deployment %s model with %s model after %d minutes',
                    deployment_id, model_id, timeout_period)
                raise TimeoutError(
                    f'Timed out replacing deployment {deployment_id} model with {model_id} model'
                    f' after {timeout_period} minutes')

            if self.status_code(status_resp) == 303:
                deployment_resp = self.v2_api_get_request(
                    urlparse(self.get_location_header(status_resp)).path)

                assert self.get_value_from_json_response(
                    deployment_resp,
                    DeploymentsKeys.DEPLOYMENT_STATUS.value) == 'active'
                break

            sleep(poll_interval)

            self.logger.info('Deployment %s model was replaced with model %s',
                             deployment_id, model_id)

    def contact_us(self,
                   topic,
                   text,
                   revision,
                   username=None,
                   invite_code=None,
                   is_signed_up=True,
                   check_status_code=True):
        """
        Sends a message to Self-Service Trial Support Team with POST /contactUs.

        Parameters
        ----------
        topic : str
            Message topic: Trial Support, Data Science, Pricing Info, Other
        text : str
            Message text
        revision : str
            App revision number, e.g. V91ed34e
        username : str
            Unauthenticated user email address
        invite_code : str
            Code query param value of inviteLink url returned in PAYG user creation response
        is_signed_up : bool
            Separate payload for (un)authenticated user
        check_status_code : bool
            Check if status code is 200 or not

        Returns
        -------
        resp : requests.models.Response
            Response object
        """
        payload = {'topic': topic,
                   'text': text,
                   'revision': revision}
        if not is_signed_up:
            payload.update({'username': username,
                            'code': invite_code})

        resp = self.internal_api_post_request(CONTACT_US,
                                              payload,
                                              check_status_code=check_status_code)
        self.logger.info(
            'Sent message "%s" with topic "%s" and revision "%s" to POST %s endpoint',
            text, topic, revision, CONTACT_US)

        return resp

    def v2_delete_deployment(self, deployment_id):
        """
        Deletes deployment DELETE api/v2/deployments/{deployment_id}.

        Parameters
        ----------
        deployment_id : str
            Deployment id
        """
        resp = self.v2_api_delete_request(f'{API_V2_DEPLOYMENTS_PATH}/{deployment_id}',
                                          check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=204,
                                actual_code=self.status_code(resp),
                                message=f'Deployment {deployment_id} was not deleted')

        self.logger.info('Deployment %s was deleted', deployment_id)

    def v2_deploy_automodel(self,
                            label,
                            project_id,
                            description='',
                            has_description=True):
        """
        Deploys Automodel.
        POST api/v2/deployments/fromProjectRecommendedModel.

        Parameters
        ----------
        label : str
            Automodel label (title)
        project_id : str
            Project id
        description : str
            Automodel description
        has_description : bool
            If Automodel has description field or not

        Returns
        -------
        automodel_id : str
            Automodel id
        """
        payload = {'description': description,
                   'label': label,
                   'projectId': project_id}

        if not has_description:
            payload.pop('description')

        resp = self.v2_api_post_request(API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH,
                                        payload,
                                        check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Automodel for project {project_id} was not created')
        automodel_id = self.get_value_from_json_response(
            resp,
            FromRecommendedModelKeys.AUTOMODEL_ID.value)

        self.logger.info('Automodel %s for project %s was created',
                         automodel_id, project_id)
        return automodel_id

    def v2_add_feature_flag(self, flag, flag_value=True):
        """
        Adds a feature flag to  a user.
        PATCH api/v2/users/{user_id}/.

        Parameters
        ----------
        flag : str
            Feature flag name
        flag_value : bool
            Enable or disable a feature flag
        """
        payload = {'permissionsDiff': {flag: flag_value}}

        resp = self.v2_api_admin_patch_request(f'{API_V2_PATH}/users/{self.user_id}/',
                                               payload,
                                               check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=204,
                                actual_code=self.status_code(resp),
                                message=f'Feature flag {flag} with value {flag_value} '
                                        f'was not added for user {self.user_id}')

        self.logger.info('Feature flag %s with value %r was added to user %s',
                         flag, flag_value, self.user_id)

    def v2_add_feature_flags(self, flags_dict):
        """
        Adds a single or multiple feature flags to a user
        by passing a feature flags dict to 'permissionsDiff' dict.
        PATCH api/v2/users/{user_id}/.

        Parameters
        ----------
        flags_dict : dict
            Feature flags dictionary, e.g. {flag1: True, flag2: False}
        """
        payload = {'permissionsDiff': flags_dict}

        resp = self.v2_api_admin_patch_request(
            f'{API_V2_PATH}/users/{self.user_id}/',
            payload,
            check_status_code=False
        )
        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'Feature flags {flags_dict} were not added'
                    f' for user {self.user_id}'
        )
        self.logger.info(
            'Feature flags %s were added to user %s',
            flags_dict, self.user_id)

    def v2_poll_for_first_available_deployment(self, poll_interval=1, timeout_period=15):
        """
        Returns first available deployment from deployments list.

        Parameters
        ----------
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now

        Returns
        -------
        deployment_id : str
            First available deployment from deployments list
        """
        timeout = time() + 60 * timeout_period
        while True:
            resp = self.v2_api_get_request(f'{API_V2_DEPLOYMENTS_PATH}/',
                                           check_status_code=False)
            self.logger.info('Polling for the 1st available deployment. '
                             'Will stop polling in %s', time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out polling for the 1st available deployment after %d minutes',
                    timeout_period)
                raise TimeoutError(
                    f'Timed out polling for the 1st available deployment after {timeout_period} minutes')

            if self.get_response_json(resp)['count'] != 0:
                deployment_id = self.get_value_from_json_response(
                    resp, DeploymentsKeys.FIRST_DEPLOYMENT_ID.value)
                break

            sleep(poll_interval)

        self.logger.info('Deployment found: %s', deployment_id)

        return deployment_id

    def v2_poll_for_autopilot_done(self, project_id, poll_interval=5, timeout_period=40):
        """
        Wait until Automodel is finished.

        Parameters
        ----------
        project_id : str
            Project id
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now
        """
        timeout = time() + 60 * timeout_period
        while True:
            resp = self.v2_api_get_request(f'{API_V2_PATH}/projects/{project_id}/status',
                                           check_status_code=False)
            is_done = resp.json()['autopilotDone']

            self.logger.info('Polling for Autopilot for project %s to finish: %r. '
                             'Will stop polling in %s', project_id, is_done, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out polling for Autopilot for project %s to finish after %d minutes',
                    project_id, timeout_period)
                raise TimeoutError(
                    f'Timed out polling for Autopilot for project {project_id} to finish'
                    f' after {timeout_period} minutes')

            if is_done:
                break
            sleep(poll_interval)

        self.logger.info('Autopilot for project %s is done', project_id)

    def make_predictions(self, deployment_id, dataset_path):
        """
        Makes single predictions.

        Parameters
        ----------
        deployment_id : str
            Deployment id
        dataset_path : str
            Path to prediction dataset file

        Returns
        -------
        response : Response
            Response object
        """
        self.logger.info(
            'About to make single predictions against %s deployment using %s dataset',
            deployment_id, dataset_path)

        with open(dataset_path, 'rb') as dataset_file:
            resp = self.predictions_api_post_request(
                host=self.v2_get_prediction_endpoint(),
                path=f'predApi/v1.0/deployments/{deployment_id}/predictions',
                datarobot_key=self.v2_get_datarobot_key(),
                data=dataset_file,
                check_status_code=False)
        return resp

    def make_time_series_predictions(self,
                                     deployment_id,
                                     dataset_path,
                                     forecast_point,  # '2011-06-15T00:00:00Z'
                                     relax_known_in_advance_features_check=False):
        """
        Makes predictions with time series models.

        Parameters
        ----------
        deployment_id : str
            Deployment id
        dataset_path : str
            Path to prediction dataset file
        forecast_point : str
            An ISO 8601 formatted DateTime string, without timezone
        relax_known_in_advance_features_check : bool
             When True, missing values for known in advance features
             are allowed in the forecast window at prediction time

        Returns
        -------
        response : Response
            Response object
        """
        query_params = {'forecastPoint': forecast_point,
                        'relaxKnownInAdvanceFeaturesCheck': relax_known_in_advance_features_check}

        self.logger.info(
            'About to make single time series predictions against %s deployment using %s dataset',
            deployment_id, dataset_path)

        with open(dataset_path, 'rb') as dataset_file:
            resp = self.predictions_api_post_request(
                host=self.v2_get_prediction_endpoint(),
                path=f'predApi/v1.0/deployments/{deployment_id}/timeSeriesPredictions',
                query_params=query_params,
                datarobot_key=self.v2_get_datarobot_key(),
                data=dataset_file,
                check_status_code=False)
        return resp

    def make_predictions_with_explanations(self,
                                           deployment_id,
                                           dataset_path,
                                           max_codes=3,
                                           threshold_high=0.5,
                                           threshold_low=0.15):
        """
        Makes predictions with explanations.

        Parameters
        ----------
        deployment_id : str
            Deployment id
        dataset_path : str
            Path to prediction dataset file
        max_codes : int
            Max number of codes generated per prediction
        threshold_high : float
            Predictions must be above this value for Prediction Explanations to compute
        threshold_low : float
            Predictions must be below this value for Prediction Explanations to compute

        Returns
        -------
        response : Response
            Response object
        """
        query_params = {'maxCodes': max_codes,
                        'thresholdHigh': threshold_high,
                        'thresholdLow': threshold_low}

        self.logger.info('About to make single predictions with explanations '
                         'against %s deployment using %s dataset', deployment_id, dataset_path)

        with open(dataset_path, 'rb') as dataset_file:
            resp = self.predictions_api_post_request(
                host=self.v2_get_prediction_endpoint(),
                path=f'predApi/v1.0/deployments/{deployment_id}/predictionExplanations',
                query_params=query_params,
                datarobot_key=self.v2_get_datarobot_key(),
                data=dataset_file,
                check_status_code=False)
        return resp

    def v2_make_batch_predictions(self, deployment_id, dataset_id,
                                  skip_drift_tracking=True,
                                  prediction_warning_enabled=False,
                                  timeout_period=10,
                                  poll_interval=2,
                                  raise_error=True):
        """
        Starts batch predictions POST api/v2/batchPredictions/.
        Polls for predictions COMPLETED status.

        Parameters
        ----------
        deployment_id : str
            Deployment id
        dataset_id : str
            Prediction dataset id
        skip_drift_tracking : bool
            If to skip drift tracking or not
        prediction_warning_enabled : bool
            If to enable prediction warning or not
        timeout_period : int
            Stop polling in timeout_period minutes from now
        poll_interval : int
            Poll every n seconds
        raise_error : bool
            If to raise an error and stop the test or not

        Returns
        -------
        response : Response
            Predictions status url response object
        """

        payload = {'deploymentId': deployment_id,
                   'skipDriftTracking': skip_drift_tracking,
                   'predictionWarningEnabled': prediction_warning_enabled,
                   'intakeSettings': {
                       'type': 'dataset',
                       'datasetId': dataset_id}}

        resp = self.v2_api_post_request(f'{API_V2_PATH}/batchPredictions/',
                                        payload,
                                        check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Batch predictions failed: '
                                        f'deploymentId {deployment_id}, '
                                        f'datasetId {dataset_id}')
        self.logger.info(
            'Starting predictions: deploymentId %s, datasetId %s',
            deployment_id, dataset_id)

        status_url = urlparse(self.get_location_header(resp)).path

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(status_url,
                                                  allow_redirects=False,
                                                  check_status_code=False)
            actual_status = status_resp.json()['status']

            self.logger.info(
                'Making predictions: deploymentId %s, status %s. '
                'Will stop in %s minutes',
                deployment_id, actual_status, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Polling timed out in %d minutes. Predictions status: %s',
                    timeout_period, actual_status)
                if raise_error:
                    raise TimeoutError(
                        TIMEOUT_MESSAGE.format(COMPLETED_STATUS,
                                               'predictions status',
                                               actual_status,
                                               timeout_period))
                return status_resp

            if actual_status == COMPLETED_STATUS:
                self.logger.info('Predictions are done. Status %s',
                                 actual_status)
                return status_resp

            sleep(poll_interval)

    def v2_analyze_datetime_partition_column(self,
                                             project_id,
                                             datetime_partition_column,
                                             poll_interval=1,
                                             timeout_period=15):
        """
        Waits until the analysis of relationships between
        potential partition and multiseries ID columns is completed.

        Parameters
        ----------
        project_id : str
            Project id
        datetime_partition_column : str
            Date column that will be used to perform detection and validation for
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now

        Returns
        -------
        response : Response
            Response object
        """
        payload = {'datetimePartitionColumn': datetime_partition_column}

        resp = self.v2_api_post_request(f'{API_V2_PATH}/projects/{project_id}/multiseriesProperties/',
                                        payload,
                                        check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Could not analyze datetimePartitionColumn {datetime_partition_column}'
                                        f' for project {project_id}')
        self.logger.info('Starting to analyze datetimePartitionColumn "%s" for time series project %s',
                         datetime_partition_column, project_id)

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(urlparse(self.get_location_header(resp)).path,
                                                  allow_redirects=False,
                                                  check_status_code=False)
            self.logger.info('datetimePartitionColumn "%s" is being analyzed for project %s.'
                             ' Will stop polling in %s',
                             datetime_partition_column, project_id, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out polling for datetimePartitionColumn "%s" for project %s after %d minutes',
                    datetime_partition_column, project_id, timeout_period)
                raise TimeoutError(
                    f'Timed out polling for datetimePartitionColumn "{datetime_partition_column}" '
                    f'for project {project_id} after {timeout_period} minutes')

            if self.status_code(status_resp) == 303:
                break
            sleep(poll_interval)

        self.logger.info('datetimePartitionColumn "%s" was analyzed for time series project %s',
                         datetime_partition_column, project_id)

    def v2_get_deployment(self, deployment_id):
        """
        Get info about a deployment by deployment_id.
        GET api/v2/deployments/{deployment_id}.

        Parameters
        ----------
        deployment_id : str
            Deployment id

        Returns
        -------
        response : Response
            Response object
        """
        return self.v2_api_get_request(f'{API_V2_DEPLOYMENTS_PATH}/{deployment_id}')

    def v2_get_deployments(self):
        """
        Get user's deployments GET api/v2/deployments/.

        Returns
        -------
        response : Response
            Response object
        """
        return self.v2_api_get_request(f'{API_V2_DEPLOYMENTS_PATH}/')

    def v2_deployments_action_log(self, deployment_id):
        """
        Get deployment action log GET api/v2/modelDeployments/{deployment_id}/actionLog/.

        Parameters
        ----------
        deployment_id : str
            Deployment id

        Returns
        -------
        response : Response
            Response object
        """
        return self.v2_api_get_request(
            f'{API_V2_PATH}/modelDeployments/{deployment_id}/actionLog/')

    def v2_deployment_info(self, deployment_id):
        """
        Get deployment info, e.g. modelHistory.
        GET api/v2/deployments/{deployment_id}/info/.

        Parameters
        ----------
        deployment_id : str
            Deployment id

        Returns
        -------
        response : Response
            Response object
        """
        return self.v2_api_get_request(
            f'{API_V2_PATH}/deployments/{deployment_id}/info/')

    def v2_deployment_service_stats(self, deployment_id):
        """
        Get deployment predictions statistics:
        totalRequests, totalPredictions, user/server ErrorRate, responseTime etc.
        GET api/v2/deployments/{deployment_id}/serviceStats/.

        Parameters
        ----------
        deployment_id : str
            Deployment id

        Returns
        -------
        response : Response
            Response object consisting of metrics and period dicts, modelId
        """
        return self.v2_api_get_request(
            f'{API_V2_PATH}/deployments/{deployment_id}/serviceStats/')

    def v2_change_deployment_status(self, deployment_id, status,
                                    poll_interval=1, timeout_period=15):
        """
        Change deployment status from active to inactive or vice verse.
        GET api/v2/deployments/{deployment_id}/status/.

        Parameters
        ----------
        deployment_id : str
            Deployment id
        status : str
            Deployment status: active or inactive
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now
        """
        payload = {'status': status}

        resp = self.v2_api_patch_request(f'{API_V2_DEPLOYMENTS_PATH}/{deployment_id}/status/',
                                         payload,
                                         check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Deployment {deployment_id} status wasn\'t changed to {status}')

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(urlparse(self.get_location_header(resp)).path,
                                                  allow_redirects=False,
                                                  check_status_code=False)
            self.logger.info('Polling for deployment %s to become %s. Will stop polling in %s',
                             deployment_id, status, time_left(timeout))

            if time() > timeout:
                self.logger.error('Timed out polling for deployment %s to become %s after %d minutes',
                                  deployment_id, status, timeout_period)
                raise TimeoutError(
                    f'Timed out polling for deployment {deployment_id} to become {status} '
                    f'after {timeout_period} minutes')

            if self.status_code(status_resp) == 303:
                break
            sleep(poll_interval)

        self.logger.info('Deployment %s is now %s', deployment_id, status)

    def v2_create_ai_app(self,
                         app_name,
                         deployment_id,
                         app_type_id=WHAT_IF_APP_ID,
                         source_name='predictor',
                         source='deployment',
                         poll_interval=1,
                         timeout_period=20):
        """
        Creates AI App from deployment id.
        POST api/v2/applications/.

        Parameters
        ----------
        app_name : str
            Application name
        deployment_id : str
            Deployment id
        app_type_id : str
            ID of the of application to be created
        source_name : str
            Name of the source to create the app from
        source : str
            Source to create the app from
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now

        Returns
        -------
        app_id : str
            Application ID
        """
        payload = {"sources": [{'source': source,
                                'info': {'modelDeploymentId': deployment_id},
                                'name': source_name}],
                   'applicationTypeId': app_type_id,
                   'name': app_name}

        resp = self.v2_api_post_request(f'{API_V2_PATH}/applications/',
                                        payload,
                                        check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'App "{app_name}", '
                                        f'applicationTypeId: "{app_type_id}", '
                                        f'source_name: "{source_name}", '
                                        f'source: "{source}", '
                                        f'deployment_id "{deployment_id}" was not deployed')

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(urlparse(self.get_location_header(resp)).path,
                                                  allow_redirects=False,
                                                  check_status_code=False)
            self.logger.info('Polling for app %s to be deployed from %s. Will stop polling in %s',
                             app_name, deployment_id, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out polling for app %s to be deployed from %s after %d minutes',
                    app_name, deployment_id, timeout_period)
                raise TimeoutError(
                    f'Timed out polling for app {app_name} to be deployed from {deployment_id}'
                    f' after {timeout_period} minutes')

            if self.status_code(status_resp) == 303:
                app_resp = self.v2_api_get_request(
                    urlparse(self.get_location_header(status_resp)).path)

                assert self.get_value_from_json_response(
                    app_resp,
                    AppsKeys.DEPLOYMENT_STATE.value) == 'deployed'
                app_id = self.get_value_from_json_response(app_resp, AppsKeys.ID.value)

                self.logger.info('App %s with app_id %s has been deployed from %s deployment',
                                 app_name, app_id, deployment_id)
                break
            sleep(poll_interval)
        return app_id

    def v2_upload_dataset_via_url(self,
                                  url,
                                  do_snapshot=True,
                                  persist_data_after_ingest=True,
                                  poll_interval=1,
                                  timeout_period=10):
        """
        Uploads a dataset via url POST api/v2/datasets/fromURL/

        Parameters
        ----------
        url : str
            Dataset url
        do_snapshot : bool
            If to do snapshot or not
        persist_data_after_ingest : bool
            If to persist data after ingestion or not
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now

        Returns
        -------
        dataset_id : str
            Dataset ID
        """
        payload = {'url': url,
                   'doSnapshot': do_snapshot,
                   'persistDataAfterIngestion': persist_data_after_ingest}

        resp = self.v2_api_post_request(f'{API_V2_PATH}/datasets/fromURL/',
                                        payload,
                                        check_status_code=False)
        self.assert_status_code(resp,
                                expected_code=202,
                                actual_code=self.status_code(resp),
                                message=f'Dataset {url} was not uploaded')
        status_url = urlparse(self.get_location_header(resp)).path

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(status_url,
                                                  allow_redirects=False,
                                                  check_status_code=False)
            self.logger.info(
                'Uploading %s. Will stop polling in %s',
                url, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out polling for dataset %s to be uploaded'
                    ' after %d minutes', url, timeout_period)
                raise TimeoutError(TIMEOUT_MESSAGE.format(
                    url,
                    'to upload',
                    self.get_response_text(status_resp),
                    timeout_period))

            if self.status_code(status_resp) == 303:
                dataset_resp = self.v2_api_get_request(
                    urlparse(self.get_location_header(status_resp)).path)

                assert self.get_value_from_json_response(
                    dataset_resp, DatasetsDatasetIdKeys.STATE.value) == COMPLETED_STATUS

                dataset_id = self.get_value_from_json_response(
                    dataset_resp, DatasetsDatasetIdKeys.ID.value)
                self.logger.info(
                    'Dataset %s is uploaded. datasetId %s', url, dataset_id)

                return dataset_id

            sleep(poll_interval)

    def v2_get_credit_balance_summary(self):
        """
        Returns response object with user's balance summary, e.g.:
        {"creditsExpirationDate": "2021-06-11T07:22:03.818783+00:00",
        "balanceAfterLastCreditTransaction": 5,
        "lastCreditTransactionDate": "2020-12-09T07:22:03.818783+00:00",
        "currentBalance": 5}
        GET api/v2/creditsSystem/creditBalanceSummary/.

        Returns
        -------
        response : Response
            Response object with user's credits balance summary
        """
        balance_endpoint = 'creditsSystem/creditBalanceSummary/'
        resp = self.v2_api_get_request(f'{API_V2_PATH}/{balance_endpoint}')

        self.logger.info('Called GET api/v2/%s', balance_endpoint)

        return resp

    def v2_get_current_credit_balance(self):
        """
        Returns user's current credits balance

        Returns
        -------
        current_balance : int
            User's current balance
        """
        balance = self.get_value_from_json_response(
            self.v2_get_credit_balance_summary(),
            BalanceSummaryKeys.CURRENT_BALANCE.value)

        self.logger.info('Current balance: %d', balance)

        return balance

    def v2_get_credit_usage_summary(self, billing_period_start_ts, segment_by):
        """
        Get credits usage summary GET api/v2/creditsSystem/creditUsageSummary/

        Returns
        -------
        billing_period_start_ts : str
            Time, e.g. 2020-12-11T17:58:12+03:00 (+ needs to be urlencoded)
        segment_by : str
            projectName or category
        """
        credit_usage_summary_path = f'{API_V2_PATH}/creditsSystem/creditUsageSummary/'
        params = f'billingPeriodStartTs={replace_chars_if_needed(billing_period_start_ts)}&' \
                 f'segmentBy={segment_by}'
        resp = self.v2_api_get_request(credit_usage_summary_path,
                                       query_params=params)

        self.logger.info('Called GET %s', credit_usage_summary_path)

        return resp

    def poll_for_balance(self, expected_balance, timeout_period=10,
                         poll_interval=2, raise_error=True):
        """
        Polls for expected credit balance

        Parameters
        ----------
        expected_balance : int
            Expected credit balance
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now
        raise_error : bool
            If to raise an error and stop the test or not

        Returns
        -------
        actual_balance : int
            User's current balance
        """
        timeout = time() + 60 * timeout_period

        while True:
            actual_balance = self.v2_get_current_credit_balance()
            self.logger.info(
                'Polling for %d balance. Will stop polling in %s',
                expected_balance, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Balance is not %d. Timed out in %d minutes',
                    expected_balance, timeout_period)
                if raise_error:
                    raise TimeoutError(
                        TIMEOUT_MESSAGE.format(expected_balance,
                                               'balance',
                                               actual_balance,
                                               timeout_period))
                return actual_balance

            if actual_balance == expected_balance:
                self.logger.info('Stopped polling. Balance is %d',
                                 actual_balance)
                return actual_balance

            sleep(poll_interval)

    def poll_for_balance_range(self, min_balance, max_balance,
                               timeout_period=10,
                               poll_interval=2,
                               raise_error=True):
        """
        Polls for balance to be from {min_balance} to {max_balance}

        Parameters
        ----------
        min_balance : int
            Expected minimum balance
        max_balance : int
            Expected maximum balance
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now
        raise_error : bool
            If to raise an error and stop the test or not

        Returns
        -------
        actual_balance : int
            User's current balance
        """
        timeout = time() + 60 * timeout_period

        while True:
            actual_balance = self.v2_get_current_credit_balance()
            self.logger.info(
                'Polling for balance from %d to %d. Will stop polling in %s',
                min_balance, max_balance, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Balance is not from %d to %d. Timed out in %d minutes',
                    min_balance, max_balance, timeout_period)
                if raise_error:
                    # 'Expected {} {}, got {}. Timed out in {} minutes'
                    raise TimeoutError(
                        f'Expected balance to be from {min_balance} to {max_balance}, '
                        f'got {actual_balance}')
                return actual_balance

            if min_balance <= actual_balance <= max_balance:
                self.logger.info('Stopped polling. Balance is %d',
                                 actual_balance)
                return actual_balance

            sleep(poll_interval)

    def poll_for_notifications(self, expected_count, username='',
                               timeout_period=5, poll_interval=1,
                               params=None, raise_error=True):
        """
        Polls for N number of notifications

        Parameters
        ----------
        expected_count : int
            Number of notifications
        username : str
            User's username
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now
        params : str
            Query params to add to notifications url
        raise_error : bool
            If to raise an error and stop the test or not

        Returns
        -------
        resp : Response
            GET api/v2/userNotifications/ response object
        """

        timeout = time() + 60 * timeout_period

        while True:
            resp = self.v2_get_user_notifications(query_params=params)
            actual_count = self.get_value_from_json_response(
                resp,
                NfKeys.COUNT.value)
            self.logger.info(
                'Polling for %s %d notifications. Got: %d. '
                'Will stop polling in: %s',
                username, expected_count, actual_count, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Expected %d notifications, got %d. '
                    'Timed out in %d minutes',
                    expected_count, actual_count, timeout_period)
                if raise_error:
                    raise TimeoutError(
                        TIMEOUT_MESSAGE.format(expected_count,
                                               'notifications',
                                               actual_count,
                                               timeout_period))
                return resp

            if actual_count >= expected_count:
                self.logger.info(
                    'Stopped polling. Got %d notifications',
                    actual_count)
                return resp

            sleep(poll_interval)

    def v2_delete_ai_app(self, app_id):
        """
        Deletes AI App DELETE api/v2/applications/{app_id/.

        Parameters
        ----------
        app_id : str
            Application Id
        """
        resp = self.v2_api_delete_request(f'{API_V2_PATH}/applications/{app_id}/',
                                          check_status_code=False)
        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'AI App {app_id} was not deleted')

        self.logger.info('AI App %s has been deleted', app_id)

    def generate_ai_report(self, project_id, timeout_period=20, poll_interval=1):
        """
        Starts generation of AI Report and polls until it's generated.
        POST trusted/projects/{project_id}/selfServeAutopilotDocs/

        Parameters
        ----------
        project_id : str
            Project Id
        timeout_period : int
            Time in minutes when polling should stop
        poll_interval : int
            Poll every N seconds

        Returns
        -------
        report_url : str
            AI report url, e.g. /trusted/projects/{pid}/selfServeAutopilotDocs/
        """
        resp = self.internal_api_post_request(
            f'trusted/projects/{project_id}/selfServeAutopilotDocs/',
            check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=202,
            actual_code=self.status_code(resp),
            message=f'AI Report generation for project {project_id} was not started')

        timeout = time() + 60 * timeout_period  # timeout_period minutes from now
        while True:
            status_resp = self.v2_api_get_request(urlparse(self.get_location_header(resp)).path,
                                                  allow_redirects=False,
                                                  check_status_code=False)

            self.logger.info('AI Report for project %s is being generated. '
                             'Will stop polling in: %s', project_id, time_left(timeout))

            if time() > timeout:
                self.logger.error('AI Report for project %s was not generated. '
                                  'Timed out after %d minutes', project_id, timeout_period)
                raise TimeoutError(f'AI Report for project {project_id} was not generated. '
                                   f'Timed out after {timeout_period} minutes.')

            if self.status_code(status_resp) == 303:
                report_url = urlparse(self.get_location_header(status_resp)).path

                self.logger.info('Generated AI report for project %s. '
                                 'Report url: %s', project_id, report_url)
                return report_url

            sleep(poll_interval)

    def download_ai_report(self, report_url):
        """
        Calls GET /trusted/projects/{pid}/selfServeAutopilotDocs/
        and writes its content in bytes to .docx file.
        Returns report file title.

        Parameters
        ----------
        report_url : str
            AI Report url

        Returns
        -------
        report_title : str
            AI report file title. Same as it's downloaded to user's OS
        """
        resp = self.internal_api_get_request(report_url)

        content_type = self.get_response_header(resp, 'Content-Type')

        assert content_type == OFFICE_DOCUMENT_RESPONSE_HEADER, \
            f'Unexpected Content-Type response header: {content_type}. ' \
            f'{OFFICE_DOCUMENT_RESPONSE_HEADER} is expected.'

        self.logger.info('Downloaded AI report: %s', report_url)

        # parse Content-Disposition response header and get a substring between double quotes
        # replace %20 with space
        report_title = get_substring_by_pattern(
            self.get_response_header(resp, 'Content-Disposition'), '"(.*?)"').replace('%20', ' ')

        # check that report title is like 'DataRobot AI Report - 2020.06.24 - 2.54pm.docx'
        assert 'DataRobot AI Report - ' + date.today().strftime('%Y.%m.%d') \
               and '.docx' in report_title, \
            f'Unexpected report title: {report_title}'

        with open(report_title, 'wb') as report_docx:
            # write report content in bytes to .docx file
            report_docx.write(self.get_response_content(resp))

        self.logger.info('AI report bytes content has been written to %s', report_title)

        return report_title

    def v2_get_user_notifications(self, query_params=None):
        """
        Get user notifications GET api/v2/userNotifications/.

        Parameters
        ----------
        query_params : dict
            Url query params

        Returns
        -------
        response : Response
            Response object
        """
        resp = self.v2_api_get_request(f'{API_V2_PATH}/userNotifications/',
                                       query_params)

        self.logger.info('Called GET %s/userNotifications/ for user %s',
                         API_V2_PATH, self.user_id)
        return resp

    def v2_update_worker_count(self, project_id, count):
        """
        Get user notifications GET api/v2/userNotifications/.

        Parameters
        ----------
        project_id : str
            Project Id
        count : int
            Number of workers
        """
        self.v2_api_patch_request(f'{API_V2_PATH}/projects/{project_id}',
                                  request_body={'workerCount': count})

        self.logger.info('Set workerCount to %d for project %s',
                         count, project_id)

    def v2_share_project(self, project_id, username, role='OWNER'):
        """
        Share a project with another user.
        PATCH api/v2/projects/5f075dc6d789b10179ed0b78/sharedRoles/.

        Parameters
        ----------
        project_id : str
            Project Id
        username : str
            Username (email) of a user to share project with
        role : str
            Role of the user towards shared project: OWNER, USER
        """
        payload = {'includeFeatureDiscoveryEntities': False,
                   'note': f'Shared {project_id} project with {username}. Yaya!',
                   'users': [{'username': username,
                              'role': role}]}

        resp = self.v2_api_patch_request(f'{API_V2_PATH}/projects/{project_id}/sharedRoles/',
                                         payload,
                                         check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'User {self.user_id} could not share project {project_id} with {username}')

        self.logger.info('User %s shared project %s with %s',
                         self.user_id, project_id, username)

    def v2_get_notification_supported_event_types(self):
        """
        Get notifications supported event types.
        GET api/v2/userNotifications/supportedEventTypes/.

        Returns
        -------
        resp : Response
            Response object
        """
        resp = self.v2_api_get_request(f'{API_V2_PATH}/userNotifications/supportedEventTypes/')

        self.logger.info('Called GET %s/userNotifications/supportedEventTypes/ for user %s',
                         API_V2_PATH, self.user_id)
        return resp

    def v2_read_notification(self, nf_id):
        """
        Mark user notifications as read.
        PATCH api/v2/userNotifications/userNotifications/{nf_id}/.

        Parameters
        ----------
        nf_id : str
            User notification id
        """
        resp = self.v2_api_patch_request(f'{API_V2_PATH}/userNotifications/{nf_id}/',
                                         request_body={},
                                         check_status_code=False)
        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'User {self.user_id} notification {nf_id} was not read')

        self.logger.info('Read user %s notification %s', self.user_id, nf_id)

    def v2_delete_notification(self, nf_id):
        """
        Delete user notification.
        DELETE api/v2/userNotifications/{nf_id}/.

        Parameters
        ----------
        nf_id : str
            User notification id
        """
        resp = self.v2_api_delete_request(f'{API_V2_PATH}/userNotifications/{nf_id}/',
                                          check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'User {self.user_id} notification {nf_id} was not deleted')

        self.logger.info('Deleted user %s notification %s', self.user_id, nf_id)

    def v2_get_recommended_model(self):
        """
        Get project recommended model id.
        GET /projects/{project_id}/recommendedModels/.

        Returns
        -------
        model_id : str
            Recommended model id
        """
        model_id = self.get_value_from_json_response(
            self.v2_api_get_request(
                f'{API_V2_PATH}/projects/{self.project_id}/recommendedModels/'),
            RecommendedModelsKeys.RECOMMENDED_MODEL.value)

        self.logger.info('Recommended model %s for project %s',
                         model_id, self.project_id)
        return model_id

    def v2_comment(self, model_id, user_id=None, mention_user=False):
        """
        Leave a comment from Comments tab (model detailed view).
        Optionally, mention a user in the comment.
        POST api/v2/comments/.

        Parameters
        ----------
        model_id : str
            Model Id
        user_id : str
            Id of the user who will be mentioned in a comment
        mention_user : bool
            Mention a user in a comment or not

        Returns
        -------
        comment_id : str
            Comment id
        """
        payload = {'entityType': 'model',
                   'entityId': model_id,
                   'content': 'test comment ',
                   'mentions': []}
        if mention_user:
            payload.update({'content': f'<@{user_id}> ',
                            'mentions': [user_id]})

        resp = self.v2_api_post_request(
            f'{API_V2_PATH}/comments/', payload, check_status_code=False)

        comment_id = self.get_value_from_json_response(resp,
                                                       CommentsKeys.ID.value)
        if mention_user:
            self.logger.info('User %s left a comment %s and mentioned user %s',
                             self.user_id, comment_id, user_id)
        else:
            self.logger.info('User %s left a comment %s', self.user_id, comment_id)

        self.assert_status_code(
            resp,
            expected_code=201,
            actual_code=self.status_code(resp),
            message=f'User {self.user_id} did not leave a comment')

        return comment_id

    def v2_explore_pre_built_use_case(self, use_case_id):
        """
        Returns plain text pre-built projectId which was
        created by mldev-demo@datarobot.com owner user and
        shared with the user who calls
        GET api/v2/projects/{use_case_id}/fromUseCase/

        Parameters
        ----------
        use_case_id : int
            Pre-built use case id

        Returns
        -------
        project_id : str
            Pre-built projectId
        """
        resp = self.v2_api_post_request(
            f'{API_V2_PATH}/projects/{use_case_id}/fromUseCase/',
            check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=201,
            actual_code=self.status_code(resp),
            message=f'Use case {use_case_id} was not explored. ')

        project_id = self.get_response_text(resp)

        self.logger.info(
            'Explored pre-built project %s fromUseCase %s',
            project_id, str(use_case_id))

        return project_id

    def v2_get_recommended_models(self, project_id):
        """
        GET api/v2/projects/{project_id}/recommendedModels/

        Parameters
        ----------
        project_id : str
            ProjectId

        Returns
        -------
        resp : Response
            Response object
        """
        path = f'{API_V2_PATH}/projects/{project_id}/recommendedModels/'
        resp = self.v2_api_get_request(path)

        self.logger.info('Called GET %s', path)

        return resp

    def v2_create_package_from_learning_model(self, model_id, model_name,
                                              prediction_threshold=0.5):
        """
        Creates a model package from a model.
        POST api/v2/modelPackages/fromLearningModel/

        Parameters
        ----------
        model_id : str
            Model Id to create a package from
        model_name : str
            Arbitrary model name
        prediction_threshold : float
            Prediction threshold

        Returns
        -------
        package_id : str
            Model packageId
        """
        payload = {'modelId': model_id,
                   'name': model_name,
                   'predictionThreshold': prediction_threshold}
        resp = self.v2_api_post_request(
            f'{API_V2_PATH}/modelPackages/fromLearningModel/',
            payload,
            check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=201,
            actual_code=self.status_code(resp),
            message=f'Did not create model package. modelId {model_id}')

        package_id = self.get_value_from_json_response(
            resp,
            ModelsKeys.ID.value)

        self.logger.info('Created model package %s from model %s',
                         package_id, model_id)

        return package_id

    def v2_deploy_from_model_package(self, package_id,
                                     label='fromModelPackage label',
                                     timeout_period=5,
                                     poll_interval=1):
        """
        Deploys a model from a model package.
        POST api/v2/fromModelPackage/

        Parameters
        ----------
        package_id : str
            Model packageId
        label : str
            Package label
        poll_interval : int
            Poll every n seconds
        timeout_period : int
            Stop polling in timeout_period minutes from now

        Returns
        -------
        deployment_id : str
            Deployment Id
        """
        payload = {'label': label,
                   'modelPackageId': package_id}
        # defaultPredictionServerId is required for staging
        server_id = self.v2_get_prediction_server_id()
        if server_id:
            payload.update({'defaultPredictionServerId': server_id})

        resp = self.v2_api_post_request(
            f'{API_V2_DEPLOYMENTS_PATH}/fromModelPackage/',
            payload,
            check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=202,
            actual_code=self.status_code(resp),
            message=f'Could not deploy from packageId {package_id}')

        status_url = urlparse(self.get_location_header(resp)).path

        timeout = time() + 60 * timeout_period
        while True:
            status_resp = self.v2_api_get_request(
                status_url,
                allow_redirects=False,
                check_status_code=False)

            self.logger.info(
                'Deploying from packageId %s. Will stop polling in %s',
                package_id, time_left(timeout))

            if time() > timeout:
                self.logger.error(
                    'Timed out polling for deploying from packageId %s'
                    ' after %d minutes', package_id, timeout_period)
                raise TimeoutError(TIMEOUT_MESSAGE.format(
                    package_id,
                    'packageId to be deployed',
                    self.get_response_text(status_resp),
                    timeout_period))

            if self.status_code(status_resp) == 303:
                resp = self.v2_api_get_request(
                    urlparse(self.get_location_header(status_resp)).path)

                assert self.get_value_from_json_response(
                    resp,
                    DeploymentsKeys.DEPLOYMENT_STATUS.value) == 'active'

                deployment_id = self.get_value_from_json_response(
                    resp,
                    DeploymentsKeys.ID.value)

                self.logger.info(
                    'Deployed from packageId %s. deploymentId %s',
                    package_id, deployment_id)

                return deployment_id

            sleep(poll_interval)

    def v2_get_demo_use_cases(self, use_case_type='demoDatasets'):
        """
        Returns demo datasets:
        GET api/v2/demoDatasets/ or api/v2/pathfinderUseCases/
        Param use_case_type is a part of the endpoint path:
        demoDatasets or pathfinderUseCases

        Parameters
        ----------
        use_case_type : str
            'pathfinderUseCases' or 'demoDatasets'

        Returns
        -------
        resp : Response
            Response object
        """
        path = f'{API_V2_PATH}/{use_case_type}/'
        resp = self.v2_api_get_request(path)

        self.logger.info('Called GET %s', path)

        return resp

    def v2_create_invoice(self,
                          product_id,
                          address,
                          city,
                          state,
                          postal_code,
                          country='US'):
        """
        Creates invoice for a credit pack:
        GET api/v2/billing/createInvoice/

        Parameters
        ----------
        product_id : str
            Explorer or Accelerator pack productId
        address : str
            Address line, e.g. 4139 Petunia Way
        city : str
            City name
        state : str
            US state, e.g. NJ
        postal_code : str
            US postal code, e.g 12345
        country : str
            Country name. Now US only

        Returns
        -------
        resp : Response
            Response object
        """
        payload = {
            'productId': product_id,
            'addressLine1': address,
            'addressCity': city,
            'addressState': state,
            'addressPostalCode': postal_code,
            'addressCountry': country
        }
        path = f'{API_V2_PATH}/{CREATE_INVOICE_PATH}'
        resp = self.v2_api_post_request(path, payload)

        self.logger.info('Called GET %s', path)

        return resp

    def v2_get_metering_activity_uptime(self, activity_type,
                                        user_ids, start_ts, end_ts):
        """
        Returns metering activity uptime info.
        GET api/v2/admin/metering/{activity_type}/activity/?
        userIds={ids}&startTimestamp={start_ts}&endTimestamp={end_ts}

        Parameters
        ----------
        activity_type : str
            Metering activity type:
            aiappUptime, deploymentUptime, prediction, mmJob
        user_ids : str
            App2 userId or list of user ids
        start_ts : str
            Time, e.g. 2020-12-11T17:58:12+03:00
        end_ts : str
            Same format as start_ts. end_ts - start_ts must be <= 24 hours

        Returns
        -------
        resp : Response
            Response object
        """
        path = f'{API_V2_PATH}/admin/metering/{activity_type}/activity/'
        query_params = f'userIds={user_ids}&' \
                       f'startTimestamp={start_ts}&' \
                       f'endTimestamp={end_ts}'

        resp = self.v2_api_admin_get_request(path, query_params)

        self.logger.info(
            'Called GET %s?%s endpoint', path, query_params
        )
        return resp

    def v2_get_user_apps(self):
        """
        Returns user AI Apps: GET api/v2/applications/.
        Json response 'data' key is the list of apps.

        Returns
        -------
        resp : Response
            Response object
        """
        path = f'{API_V2_PATH}/applications/'
        resp = self.v2_api_get_request(path)
        self.logger.info('Called GET %s', path)
        return resp

    def v2_delete_user_apps(self):
        """Deletes user AI Apps if any using self.v2_delete_ai_app()"""

        apps = self.get_value_from_json_response(
            self.v2_get_user_apps(), 'data')

        app_ids = []
        for app in apps:
            app_ids.append(app['id'])

        if app_ids:
            for app in app_ids:
                self.v2_delete_ai_app(app)
        else:
            self.logger.info('User %s has no apps to delete',
                             self.user_id)
