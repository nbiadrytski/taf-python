from os import environ

from utils.constants import (
    STAGING_SELF_SERVICE_TEST_USER,
    DR_ACCOUNT_PORTAL_REG_METER_DATA_PATH,
    DR_ACCOUNT_PORTAL_REGISTER_PATH,
    DR_ACCOUNT_PORTAL_ADMIN_PATH,
    DR_ACCOUNT_PING_PATH,
    DR_ACCOUNT_PROFILE_PATH,
    DR_ACCOUNT_ACCOUNT_PATH,
    PORTAL_ID_QUERY_PARAM,
    DR_ACCOUNT_ROLES_PATH,
    DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
    USER_PASSWORD,
    AUTH0_TOKEN_PATH,
    EMAIL_QUERY_PARAM,
    DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
    DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
    DR_ACCOUNT_PORTAL_CREATE_CHECKOUT_PATH,
    DR_ACCOUNT_PORTAL_REG_PURCHASE_PATH,
    DRAP_UPDATE_CREDIT_EXPIRATION_PATH,
    DRAP_PROCESS_EXPIRED_PACKS_PATH,
    DRAP_CHECKOUT_HISTORY_PATH,
    PORTAL_ID_KEY,
    PROD_DRAP_ADMIN_USER
)
from utils.http_utils import ApiClient
from utils.errors import FailedToRegisterDrAccountPortalUserException
from utils.data_enums import (
    DrapRegisterUserKeys,
    CreditPackKeys,
    Auth0Keys,
    Envs,
    EnvVars
)


GET_INFO_LOG_MESSAGE = 'Called DR Account Portal GET %s endpoint. portalId %s'
GET_EMAIL_INFO_LOG_MESSAGE = 'Called DR Account Portal GET %s endpoint. email %s'
POST_INFO_LOG_MESSAGE = 'Called POST %s endpoint. Payload: %s'
NO_PORTAL_ID_LOG_MESSAGE = 'Trying to call DR Account Portal GET %s endpoint without portalId query param'
DEBUG_LOG_MESSAGE = 'RESPONSE: %s'
ACCESS_TOKEN_LOG_MESSAGE = 'Generated Auth0 access token %s for user %s'


class DrAccountPortalClient(ApiClient):
    """
    DataRobot Account Portal app actions.
    See the project details in PBMP-2397.

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
    portal_id : str
        Portal id of a registered DataRobot Account Portal user
    auth0_auth_token : str
        DR Account Portal user auth0 bearer token
    admin_auth0_token : str
        DR Account Portal admin auth0 bearer token
    """
    def __init__(self, env_params, session=None):
        super().__init__(env_params, session)

        self.portal_id = None
        self.auth0_auth_token = None

        if Envs.DR_ACCOUNT_STAGING.value == env_params[1]:
            self.admin_auth0_token = self.create_user_auth0_token_staging(
                username=STAGING_SELF_SERVICE_TEST_USER,
                auth0_client_id=environ[EnvVars.AUTH0_CLIENT_ID_STAGING.value],
                auth0_client_secret=environ[EnvVars.AUTH0_CLIENT_SECRET_STAGING.value]
            )
        else:
            self.admin_auth0_token = self.create_user_auth0_token_prod(
                username=PROD_DRAP_ADMIN_USER,
                password=environ[EnvVars.DRAP_ADMIN_PASSWORD_PROD.value],
                auth0_client_id=environ[EnvVars.AUTH0_CLIENT_ID_PROD.value],
                auth0_client_secret=environ[EnvVars.AUTH0_CLIENT_SECRET_PROD.value]
            )

    def register_user(self,
                      username,
                      first_name,
                      last_name,
                      auto_ml=True,
                      paxata=True,
                      lang='En',
                      phone='123-456-7890',
                      company='Company',
                      industry='media',
                      country='US',
                      state='FL',
                      linkedin='https://test.linkedin.com',
                      github='https://test.github.com',
                      kaggle='https://test.kaggle.com',
                      add_profile_info=False,
                      add_social_info=False):
        """
        Registers PayAsYouGoUser to DataRobot Account Portal
        and assigns registered user portalId to portal_id attribute.

        Parameters
        ----------
        username : str
            User's email address. 254 characters
        first_name : str
            User's first name. 255 characters
        last_name : str
            User's last name. 255 characters
        add_profile_info : dict
            Include platform, language, phoneNumber, company, industry,
            country and state optional fields into payload
        add_social_info : dict
            Include optional socialProfiles dict (linkedin, github, kaggle)
            into payload
        auto_ml : bool
            User has access to AutoML or not
        paxata : bool
            User has access to Paxata or not
        lang : str
            User's language
        phone : str
            User's phone number. 20 characters
        company : str
            User's company. 255 characters
        industry : str
            User's industry
        country : str
            User's country. 2 characters only
        state : str
            User's state. 2 characters only
        linkedin : str
            User's linkedin profile url. Must be a URL with http(s)://
        github : str
            User's github profile url. Must be a URL with http(s)://
        kaggle : str
            User's kaggle profile url. Must be a URL with http(s)://

        Returns
        -------
        portal_id : int
            Registered user portalId
        """
        payload = {'email': username,
                   'firstName': first_name,
                   'lastName': last_name}
        if add_profile_info:
            payload.update({'platform': {'AutoML': auto_ml,
                                         'Paxata': paxata},
                            'language': lang,
                            'phoneNumber': phone,
                            'company': company,
                            'industry': industry,
                            'country': country,
                            'state': state})
        if add_social_info:
            payload.update({'socialProfiles': {'linkedin': linkedin,
                                               'github': github,
                                               'kaggle': kaggle}})

        resp = self.dr_account_admin_post_request(DR_ACCOUNT_PORTAL_REGISTER_PATH,
                                                  payload)
        try:
            self.portal_id = self.get_value_from_json_response(
                resp, DrapRegisterUserKeys.PORTAL_ID.value)
            self.logger.info(
                'User %s registered to DR Account Portal. portalId: %s',
                username, self.portal_id)
        except KeyError:
            raise FailedToRegisterDrAccountPortalUserException(
                username,
                self.get_response_text(resp))

        return resp

    def admin_register(self, payload, set_portal_id=False):
        """
        Calls POST api/admin/registerUser endpoint with arbitrary payload
        to register a user into Datarobot Account Portal.

        Parameters
        ----------
        payload : dict
            Request body
        set_portal_id : bool
            If to assign portal_id to DrAccountPortalClient portal_id attribute

        Returns
        -------
        resp: Response
            Response object
        """
        resp = self.dr_account_admin_post_request(DR_ACCOUNT_PORTAL_REGISTER_PATH,
                                                  payload,
                                                  check_status_code=False)

        self.logger.info('Called POST %s endpoint. Payload: %s',
                         DR_ACCOUNT_PORTAL_REGISTER_PATH, payload)

        if self.status_code(resp) == 200 and set_portal_id:
            self.portal_id = self.get_value_from_json_response(
                resp, DrapRegisterUserKeys.PORTAL_ID.value)

        return resp

    def admin_register_metering_data(self, payload, check_status_code=True):
        """
        POST api/admin/creditsSystem/registerMeteringData endpoint with arbitrary payload.

        Parameters
        ----------
        payload : dict
            Request body
        check_status_code : bool
            If to check request status code or not

        Returns
        -------
        resp: Response
            Response object
        """
        if not check_status_code:
            self.logger.info(
                'Trying to register metering data.\nPayload: %s', payload)
            return self.dr_account_admin_post_request(DR_ACCOUNT_PORTAL_REG_METER_DATA_PATH,
                                                      payload,
                                                      check_status_code=False)

        resp = self.dr_account_admin_post_request(DR_ACCOUNT_PORTAL_REG_METER_DATA_PATH,
                                                  payload,
                                                  check_status_code=False)
        self.assert_status_code(
            resp,
            expected_code=201,
            actual_code=self.status_code(resp),
            message=f'Metering data was not registered.\nPayload: {payload}')

        self.logger.info('Registered metering data. Payload %s', payload)

        return resp

    def delete_user(self, portal_id):
        """
        DELETE api/admin/deleteUser endpoint to delete a user.

        Parameters
        ----------
        portal_id : int
            User portalId

        Returns
        -------
        resp: Response
            Response object
        """
        resp = self.dr_account_admin_delete_request(
            f'{DR_ACCOUNT_PORTAL_ADMIN_PATH}/deleteUser', request_body={'portalId': portal_id},
            check_status_code=False)

        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'Did not delete DR Account Portal user with portalId {portal_id}')

        self.logger.info('Deleted DR Account Portal user. portalId: %s', portal_id)

        return resp

    def validate_auth(self, modify_header=True, header=None):
        """
        Returns GET api/validateAuth response.

        Parameters
        ----------
        modify_header : bool
            If to modify request header or not
        header : dict
            Header to add or replace the current one

        Returns
        -------
        resp : Response
            GET /api/validateAuth response object
        """
        log_message = 'Called DR Account Portal GET %s endpoint'

        if modify_header:
            resp = self.dr_account_request.get_request(path=DR_ACCOUNT_PING_PATH,
                                                       headers=header)
            self.logger.info(log_message, DR_ACCOUNT_PING_PATH)
            self.logger.debug(DEBUG_LOG_MESSAGE, self.get_response_text(resp))

            return resp

        resp = self.dr_account_admin_get_request(path=DR_ACCOUNT_PING_PATH)

        self.logger.info(log_message, DR_ACCOUNT_PING_PATH)
        self.logger.debug(DEBUG_LOG_MESSAGE, self.get_response_text(resp))

        return resp

    def get_profile(self, portal_id, check_status_code=True):
        """
        Returns user profile info.
        GET api/account/profile?portalId={portal_id}.

        Parameters
        ----------
        portal_id : int
            portalId query param
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if portal_id is None:
            self.logger.info(NO_PORTAL_ID_LOG_MESSAGE, DR_ACCOUNT_PROFILE_PATH)

            return self.dr_account_get_request(DR_ACCOUNT_PROFILE_PATH,
                                               check_status_code=check_status_code)
        resp = self.dr_account_get_request(
            DR_ACCOUNT_PROFILE_PATH,
            query_params=PORTAL_ID_QUERY_PARAM.format(portal_id),
            check_status_code=check_status_code)

        self.logger.info(GET_INFO_LOG_MESSAGE, DR_ACCOUNT_PROFILE_PATH, str(portal_id))

        return resp

    def get_account(self, portal_id, check_status_code=True):
        """
        Returns user account info.
        GET api/account?portalId={portal_id}.

        Parameters
        ----------
        portal_id : int
            portalId query param
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if portal_id is None:
            self.logger.info(NO_PORTAL_ID_LOG_MESSAGE, DR_ACCOUNT_ACCOUNT_PATH)

            return self.dr_account_get_request(DR_ACCOUNT_ACCOUNT_PATH,
                                               check_status_code=check_status_code)
        resp = self.dr_account_get_request(
            DR_ACCOUNT_ACCOUNT_PATH,
            query_params=PORTAL_ID_QUERY_PARAM.format(portal_id),
            check_status_code=check_status_code)

        self.logger.info(GET_INFO_LOG_MESSAGE, DR_ACCOUNT_ACCOUNT_PATH, str(portal_id))

        return resp

    def get_credit_usage_details(self, start_ts, end_ts,
                                 portal_id=None,
                                 email=None,
                                 metering_type=None,
                                 offset=None,
                                 limit=None,
                                 check_status_code=True):
        """
        Returns user credit usage details.
        GET /api/creditsSystem/creditUsageDetails.

        Parameters
        ----------
        start_ts : str
            Billing start date in ISO format %Y-%m-%dT%H:%M:%S%z,
            e.g. 2020-08-07T08:00:00Z (obligatory param)
        end_ts : str
            Billing end date in ISO format %Y-%m-%dT%H:%M:%S%z,
            e.g. 2020-08-07T08:00:00Z (obligatory param)
        portal_id : int
            DR Account Portal user portalId. Ether portalId or email is required
        email : str
            Username (url-encoded email). Ether portalId or email is required
        metering_type : str
            Options: mmJob, prediction, deploymentUptime
        offset : int
            Number of records to skip
        limit : int
            Limit to N records
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        params = f'&billingPeriodStartTs={start_ts}&billingPeriodEndTs={end_ts}'

        if start_ts is None:
            params = f'&billingPeriodEndTs={end_ts}'
        if end_ts is None:
            params = f'&billingPeriodStartTs={start_ts}'
        if metering_type is not None:
            params = f'{params}&meteringType={metering_type}'
        if offset is not None:
            params = f'{params}&offset={offset}'
        if limit is not None:
            params = f'{params}&limit={limit}'

        if email is not None:
            resp = self.dr_account_get_request(
                DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
                query_params=EMAIL_QUERY_PARAM.format(email) + params,
                check_status_code=check_status_code)
            self.logger.info(
                GET_EMAIL_INFO_LOG_MESSAGE, DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH, str(email))
            return resp

        resp = self.dr_account_get_request(
            DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH,
            query_params=PORTAL_ID_QUERY_PARAM.format(portal_id) + params,
            check_status_code=check_status_code)
        self.logger.info(
            GET_INFO_LOG_MESSAGE, DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH, str(portal_id))
        return resp

    def get_balance_summary(self, email=None, check_status_code=True):
        """
        Returns user credit balance summary.
        GET /api/creditsSystem/creditBalanceSummary.

        Parameters
        ----------
        email : str
            Username (url-encoded email). Ether portalId or email is required
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if email is not None:
            resp = self.dr_account_get_request(DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
                                               query_params=EMAIL_QUERY_PARAM.format(email),
                                               check_status_code=check_status_code)
            self.logger.info(
                GET_EMAIL_INFO_LOG_MESSAGE, DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH, str(email))
            return resp

        resp = self.dr_account_get_request(DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH,
                                           query_params=PORTAL_ID_QUERY_PARAM.format(self.portal_id),
                                           check_status_code=check_status_code)
        self.logger.info(
            GET_INFO_LOG_MESSAGE, DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH, str(self.portal_id))
        return resp

    def get_checkout_history(self,
                             email=None,
                             check_status_code=True):
        """
        Returns a list of user Credits System checkouts.
        GET api/billing/getCheckoutHistory?portalId/email={portalId/email}

        Parameters
        ----------
        email : str
            Username (url-encoded email).
            Ether portalId or email is required
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object, e.g.:
            [
            {"clientReferenceId": "85dda68d-0a2e-42b5-8b75-2b1e43ce34c6",
              "portalId": "08615f92-505f-42e7-b921-db36da4afece",
              "created": "2021-02-09T08:39:09.720615+00:00",
              "checkoutSessionId": "cs_test_a1G4z9WqV...",
              "productId": "prod_IUexvR3CTuX9Vg",
              "price": "$99.99",
              "status": "PENDING_TRANSACTION",
              "productName": "EXPLORER_PACK",
              "productDescription": "4000 AI Platform Credits, etc,"},
            ]
        """
        if email is not None:
            resp = self.dr_account_get_request(
                DRAP_CHECKOUT_HISTORY_PATH,
                query_params=EMAIL_QUERY_PARAM.format(email),
                check_status_code=check_status_code
            )
            self.logger.info(GET_EMAIL_INFO_LOG_MESSAGE,
                             DRAP_CHECKOUT_HISTORY_PATH,
                             str(email))
            return resp

        resp = self.dr_account_get_request(
            DRAP_CHECKOUT_HISTORY_PATH,
            query_params=PORTAL_ID_QUERY_PARAM.format(self.portal_id),
            check_status_code=check_status_code
        )
        self.logger.info(GET_INFO_LOG_MESSAGE,
                         DRAP_CHECKOUT_HISTORY_PATH,
                         str(self.portal_id))
        return resp

    def update_profile(self, payload, portal_id=None, check_status_code=True):
        """
        Updates user profile info.
        PATCH /api/account/profile.

        Parameters
        ----------
        payload : dict
            Request body (profile fields)
        portal_id : int
            Different portalId from self.portalId of the user to be updated.
            Default portal_id in payload is self.portalId
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if portal_id is not None:
            payload = {'portalId': portal_id, **payload}

        if check_status_code:
            resp = self.dr_account_patch_request(DR_ACCOUNT_PROFILE_PATH,
                                                 payload)
            self.logger.info('Updated DR Account Portal user profile: %s', payload)
            return resp

        self.logger.info('Trying to update DR Account Portal user profile: %s', payload)
        resp = self.dr_account_patch_request(DR_ACCOUNT_PROFILE_PATH,
                                             payload,
                                             check_status_code=False)
        return resp

    def admin_adjust_balance(self, value, reason='out of credits',
                             email=None, check_status_code=True):
        """
        Adjusts user Credits System balance as an Admin user.
        PUT api/admin/creditsSystem/adjustBalance.

        Parameters
        ----------
        email : str
            DR Account Portal username
        value : float
            Value to adjust
        reason : str
            Adjustment reason
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        payload = {'portalId': self.portal_id,
                   'value': value,
                   'reason': reason}
        user_id_type = payload['portalId']
        if email is not None:
            payload = {'email': email,
                       'value': value,
                       'reason': reason}
            user_id_type = payload['email']

        if check_status_code:
            resp = self.dr_account_admin_put_request(DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
                                                     payload,
                                                     check_status_code=False)
            self.assert_status_code(resp,
                                    expected_code=201,
                                    actual_code=self.status_code(resp),
                                    message=f'Did not adjust balance for user {user_id_type}')
            self.logger.info('Adjusted balance %s for user %s ', str(value), user_id_type)
            return resp

        self.logger.info('Trying to adjust balance %s for user %s ', str(value), user_id_type)
        return self.dr_account_admin_put_request(DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH,
                                                 payload,
                                                 check_status_code=False)

    def admin_create_checkout(self,
                              product_id,
                              quantity=1,
                              success_url='https://success.com',
                              cancel_url='https://cancel.com',
                              email=None):
        """
        Billing admin route to create a Stripe checkout.
        Creates a record in purchase_log table with PENDING_TRANSACTION status.
        POST api/billing/createCheckout.

        Parameters
        ----------
        email : str
            DR Account Portal username
        product_id : str
            product_id value (credit pack) from product_price_map table
        quantity : int
            Credit pack quantity
        success_url : str
            Checkout success url
        cancel_url : str
            Checkout cancel url
        email : str
            DR Account Portal username

        Returns
        -------
        client_ref_id : str
            clientReferenceId - purchaseId from user_credit_packs table
        """
        payload = {
            PORTAL_ID_KEY: self.portal_id,
            'productId': product_id,
            'quantity': quantity,
            'successUrl': success_url,
            'cancelUrl': cancel_url
        }
        user_id_type = payload[PORTAL_ID_KEY]

        if email is not None:
            del payload[PORTAL_ID_KEY]
            payload.update({'email': email})
            user_id_type = payload['email']

        resp = self.dr_account_post_request(
            DR_ACCOUNT_PORTAL_CREATE_CHECKOUT_PATH,
            payload
        )
        client_ref_id = self.get_value_from_json_response(
            resp,
            CreditPackKeys.CLIENT_REF_ID.value
        )
        self.logger.info(
            'User %s checked out productId %s. clientReferenceId %s',
            user_id_type, product_id, client_ref_id
        )
        return client_ref_id

    def admin_register_credit_purchase(self,
                                       value,
                                       purchase_transaction_id,
                                       purchase_transaction_ts,
                                       email=None):
        """
        Credit system admin route to register credit purchase.
        POST api/admin/creditsSystem/registerCreditPurchase.

        Parameters
        ----------
        value : float
            Amount of credits that will be granted to a user
        purchase_transaction_id : str
            clientReferenceId returned by POST api/billing/createCheckout
        purchase_transaction_ts : str
            Purchase timestamp, e.g. 2021-02-09T08:39:09+00:00
        email : str
            DR Account Portal username

        Returns
        -------
        recordId : str
            Stored as ledger_id in user_credit_packs table
        """
        payload = {
            PORTAL_ID_KEY: self.portal_id,
            'value': value,
            'purchaseTransactionId': purchase_transaction_id,
            'purchaseTransactionTs': purchase_transaction_ts
        }
        user_id_type = payload[PORTAL_ID_KEY]

        if email is not None:
            del payload[PORTAL_ID_KEY]
            payload.update({'email': email})
            user_id_type = payload['email']

        resp = self.dr_account_admin_post_request(
            DR_ACCOUNT_PORTAL_REG_PURCHASE_PATH,
            payload,
            check_status_code=False
        )
        self.assert_status_code(
            resp,
            expected_code=201,
            actual_code=self.status_code(resp),
            message=f'Did not register purchase for user {user_id_type}'
        )
        record_id = self.get_value_from_json_response(
            resp, CreditPackKeys.RECORD_ID.value
        )
        self.logger.info(
            'Registered credit purchase for user %s with value %f. '
            'recordId %s', user_id_type, value, record_id
        )
        return record_id

    def admin_update_credits_expiration(self,
                                        expiration_ts,
                                        purchase_id=None):
        """
        Updates user's all credits packs expiration timestamp.
        Updates specific credit pack timestamp if purchase_id is passed.
        PUT api/admin/creditSystem/updateCreditPacksExpirationTimestamp.

        Parameters
        ----------
        expiration_ts : str
            Credit pack new expiration timestamp,
            e.g. 2019-01-02T03:00:00+00:00
        purchase_id : str
            purchase_id column value from user_credit_packs table
        """
        payload = {
            PORTAL_ID_KEY: self.portal_id,
            'expirationTs': expiration_ts
        }
        if purchase_id is not None:
            payload.update({'purchaseId': purchase_id})

        resp = self.dr_account_admin_put_request(
            DRAP_UPDATE_CREDIT_EXPIRATION_PATH,
            payload,
            check_status_code=False
        )
        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'Credit expiration was not updated to {expiration_ts}'
                    f'. portalId {self.portal_id}'
        )
        self.logger.info('Updated credit expiration to %s. portalId %s',
                         expiration_ts, self.portal_id)

    def admin_process_expired_credits(self):
        """
        Looks for credits packs with expiration_ts < now.
        Sets balance to 0 for users with expired credit packs.
        PUT api/admin/creditsSystem/processExpiredPacks.
        """
        resp = self.dr_account_admin_put_request(
            DRAP_PROCESS_EXPIRED_PACKS_PATH,
            check_status_code=False
        )
        self.assert_status_code(
            resp,
            expected_code=204,
            actual_code=self.status_code(resp),
            message=f'Expired credits packs processing failed'
        )
        self.logger.info('Processed expired credits packs')

    def update_account(self, payload, portal_id=None, check_status_code=True):
        """
        Updates user account info.
        PATCH /api/account.

        Parameters
        ----------
        payload : dict
            Request body (account fields)
        portal_id : int
            Different portalId from self.portalId of the user to be updated.
            Default portal_id in payload is self.portalId
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if portal_id is not None:
            payload = {'portalId': portal_id, **payload}

        if check_status_code:
            resp = self.dr_account_patch_request(DR_ACCOUNT_ACCOUNT_PATH,
                                                 payload)
            self.logger.info('Updated DR Account Portal user account: %s', payload)
            return resp

        self.logger.info('Trying to update DR Account Portal user account: %s', payload)
        resp = self.dr_account_patch_request(DR_ACCOUNT_ACCOUNT_PATH,
                                             payload,
                                             check_status_code=False)
        return resp

    def admin_update_role(self, payload, portal_id=None, check_status_code=True):
        """
        Updates user role PATCH api/role.

        Parameters
        ----------
        payload : dict
            Request body (account fields)
        portal_id : int
            Different portalId from self.portalId of the user to be updated.
            Default portal_id in payload is self.portalId
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if portal_id is not None:
            payload = {'portalId': portal_id, **payload}

        if check_status_code:
            resp = self.dr_account_admin_patch_request(DR_ACCOUNT_ROLES_PATH,
                                                       payload)
            self.logger.info('Updated DR Account Portal user role: %s', payload)
            return resp

        self.logger.info('Trying to update DR Account Portal user role: %s', payload)
        resp = self.dr_account_admin_patch_request(DR_ACCOUNT_ROLES_PATH,
                                                   payload,
                                                   check_status_code=False)
        return resp

    def admin_get_role(self, portal_id, check_status_code=True):
        """
        Returns Admin GET api/roles?portalId={portal_id} response.

        Parameters
        ----------
        portal_id : int
            portalId query param
        check_status_code : bool
            If to check status code or not

        Returns
        -------
        resp : Response
            Response object
        """
        if portal_id is None:
            self.logger.info(NO_PORTAL_ID_LOG_MESSAGE, DR_ACCOUNT_ROLES_PATH)

            return self.dr_account_admin_get_request(DR_ACCOUNT_ROLES_PATH,
                                                     check_status_code=check_status_code)
        resp = self.dr_account_admin_get_request(
            DR_ACCOUNT_ROLES_PATH,
            query_params=PORTAL_ID_QUERY_PARAM.format(portal_id),
            check_status_code=check_status_code)

        self.logger.info(GET_INFO_LOG_MESSAGE, DR_ACCOUNT_ROLES_PATH, str(portal_id))

        return resp

    def create_user_auth0_token_staging(self,
                                        username,
                                        auth0_client_id,
                                        auth0_client_secret):
        """
        Returns auth0 access token for staging env.
        Access token is required for each DRAP API call.
        Token generation:
        https://auth0.com/docs/api-auth/tutorials/password-grant#ask-for-a-token
        Auth0 staging settings:
        https://manage.auth0.com/dashboard/us/datarobotdev/apis/5ece751cd828cf001ce62c1a/settings

        Parameters
        ----------
        username : str
            PayAsYouGoUser's email address
        auth0_client_id : str
            Staging Auth0 client id
        auth0_client_secret : str
            Staging Auth0 client secret

        Returns
        -------
        auth0_auth_token : str
            Staging Auth0 access token
        """
        payload = {
            'grant_type': 'password',
            'username': username,
            'password': USER_PASSWORD,
            'audience': 'https://staging.account.datarobot.com',
            'scope': 'read:sample',
            'client_id': auth0_client_id,
            'client_secret': auth0_client_secret
        }
        resp = self.auth0_post_request(
            AUTH0_TOKEN_PATH, payload
        )
        self.auth0_auth_token = self.get_value_from_json_response(
            resp,
            Auth0Keys.ACCESS_TOKEN.value
        )
        self.logger.info(ACCESS_TOKEN_LOG_MESSAGE,
                         self.auth0_auth_token, username)

        return self.auth0_auth_token

    def create_user_auth0_token_prod(self,
                                     username,
                                     password,
                                     auth0_client_id,
                                     auth0_client_secret):
        """
        Returns auth0 access token for prod env.
        Access token is required for each DRAP API call.

        Parameters
        ----------
        username : str
            PayAsYouGoUser's email address
        password : str
            User password
        auth0_client_id : str
            Prod Auth0 client id
        auth0_client_secret : str
            Prod Auth0 client secret

        Returns
        -------
        auth0_auth_token : str
            Prod Auth0 access token
        """
        payload = {
            'client_id': auth0_client_id,
            'client_secret': auth0_client_secret,
            'username': username,
            'password': password,
            'audience': 'https://account.datarobot.com',
            'grant_type': 'http://auth0.com/oauth/grant-type/password-realm',
            'realm': 'Username-Password-Authentication',
        }
        resp = self.auth0_post_request(
            AUTH0_TOKEN_PATH, payload
        )
        self.auth0_auth_token = self.get_value_from_json_response(
            resp,
            Auth0Keys.ACCESS_TOKEN.value
        )
        self.logger.info(ACCESS_TOKEN_LOG_MESSAGE,
                         self.auth0_auth_token, username)

        return self.auth0_auth_token
