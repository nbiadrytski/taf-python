"""Contains common variables and constants used across the project."""

import os
from pathlib import Path

from utils.data_enums import FeatureFlags


THIS_FILE_PARENT_DIR = Path(__file__).parent.parent.absolute()


# DATASETS
TEN_K_DIABETES_XLSX_DATASET = 'http://s3.amazonaws.com/datarobot_data_science/test_data/10k_diabetes.xlsx'
TEN_K_DIABETES_PREDICTION_DATASET_URL = 'https://s3.amazonaws.com/datarobot-use-case-datasets/10kDiabetesScoring.csv'
DATASET_42_MB = 'https://s3.amazonaws.com/datarobot_public_datasets/burncpu_train_OTP.csv'
DATASET_88_MB = 'https://s3.amazonaws.com/datarobot_public_datasets/kiva_loans_train.csv'


TEN_K_DIABETES_PROJECT_NAME = '10k_diabetes.csv'
DATASETS_PATH = 'data/datasets/'
TEN_K_DIABETES_DATASET = os.path.join(THIS_FILE_PARENT_DIR, DATASETS_PATH, TEN_K_DIABETES_PROJECT_NAME)
TEN_K_DIABETES_PREDICTION_DATASET = os.path.join(THIS_FILE_PARENT_DIR, DATASETS_PATH, '10kDiabetesScoring.csv')
TEN_K_DIABETES_TARGET = 'readmitted'

# TEST FILES
TEST_FILES_PATH = 'data/test_data/'
CREDIT_DETAILS_NO_REQUIRED_FIELDS_RESP = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH,
    'credit_details_no_required_fields_resp.json')
INVALID_CREDITS_FIELDS_RESP = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH,
    'invalid_credits_fields_response.json')
AI_REPORT_CONTENT = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'ai_report_content')
AI_REPORT_TABLES_DATA = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'ai_report_tables_data')
DOCS_SEARCH_ALL = os.path.join(
    THIS_FILE_PARENT_DIR, TEST_FILES_PATH, 'docs_search_all.json')

ARIMA_TIME_SERIES_DATASET = os.path.join(THIS_FILE_PARENT_DIR, DATASETS_PATH, 'arima1_train.csv')
ARIMA_TIME_SERIES_TARGET = 'y'

REGRESSION_HEALTH_EXPEND_DATASET = os.path.join(THIS_FILE_PARENT_DIR, DATASETS_PATH, 'HealthExpendOP_train.csv')
REGRESSION_HEALTH_EXPEND_PREDICTION_DATASET = os.path.join(
    THIS_FILE_PARENT_DIR, DATASETS_PATH, 'HealthExpendOP_test.csv')
REGRESSION_HEALTH_EXPEND_TARGET = 'EXPENDOP'

ANIMALS_DATASET = os.path.join(THIS_FILE_PARENT_DIR, DATASETS_PATH, 'animals.csv')
ANIMALS_TARGET = 'visible'

# API PATHS
API_V2_PATH = 'api/v2'
API_V2_DEPLOYMENTS_PATH = 'api/v2/deployments'
API_V2_DEPLOYMENTS_FROM_PROJECT_RECOMMENDED_MODEL_PATH = 'api/v2/deployments/fromProjectRecommendedModel/'
CONTACT_US = 'contactUs'  # POST /contactUS
CREATE_INVOICE_PATH = 'billing/createInvoice/'

# DataRobot Account Portal API paths
DR_ACCOUNT_PORTAL_ADMIN_PATH = 'api/admin'
DR_ACCOUNT_PORTAL_REGISTER_PATH = DR_ACCOUNT_PORTAL_ADMIN_PATH + '/registerUser'
DR_ACCOUNT_PORTAL_REG_METER_DATA_PATH = DR_ACCOUNT_PORTAL_ADMIN_PATH + '/creditsSystem/registerMeteringData'
DR_ACCOUNT_PORTAL_ADJUST_BALANCE_PATH = DR_ACCOUNT_PORTAL_ADMIN_PATH + '/creditsSystem/adjustBalance'
DR_ACCOUNT_PORTAL_CREATE_CHECKOUT_PATH = 'api/billing/createCheckout'
DR_ACCOUNT_PORTAL_REG_PURCHASE_PATH = DR_ACCOUNT_PORTAL_ADMIN_PATH + '/creditsSystem/registerCreditPurchase'
DRAP_UPDATE_CREDIT_EXPIRATION_PATH = DR_ACCOUNT_PORTAL_ADMIN_PATH + \
                                     '/creditSystem/updateCreditPacksExpirationTimestamp'
DRAP_PROCESS_EXPIRED_PACKS_PATH = DR_ACCOUNT_PORTAL_ADMIN_PATH + '/creditsSystem/processExpiredPacks'
DRAP_CHECKOUT_HISTORY_PATH = 'api/billing/getCheckoutHistory'
DR_ACCOUNT_PROFILE_PATH = 'api/account/profile'
DR_ACCOUNT_ACCOUNT_PATH = 'api/account'
DR_ACCOUNT_PING_PATH = 'api/validateAuth'
DR_ACCOUNT_ROLES_PATH = 'api/account/roles'
DR_ACCOUNT_CREDIT_USAGE_DETAILS_PATH = 'api/creditsSystem/creditUsageDetails'
DR_ACCOUNT_PORTAL_CREDIT_BALANCE_PATH = 'api/creditsSystem/creditBalanceSummary'

PORTAL_ID_KEY = 'portalId'
PORTAL_ID_QUERY_PARAM = 'portalId={}'
EMAIL_QUERY_PARAM = 'email={}'
AUTH0_TOKEN_PATH = 'oauth/token'

STAGING_SELF_SERVICE_TEST_USER = 'staging_self_service_api_tester@test.com'
PROD_DRAP_ADMIN_USER = 'portal-admin@datarobot.com'
# It is important to use one of the existing emails to avoid email bouncing on AWS!
TEST_USER_EMAIL = 'staging.test.user+self_service_api_tests_{}@datarobot.com'
USER_PASSWORD = 'Testing123!!!'

STATUS_CODE = 'Status code: {}'
STATUS_ERROR_TEXT = 'Expected status code: {}, got: {}'
LIMITED_ACCESS_MESSAGE = '"message": "Your access to this functionality is limited"'
LIMITED_ACCESS_RESP_CODE = '403. Response'
LIMITED_ACCESS_ERROR_CODE = '"errorCode": 402'
ASSERT_ERRORS = 'errors occurred:\n{}'
ERROR_STATUS_CODE_RESPONSE = '\nStatus code: {}.\nResponse: {}'
ERROR_JSON_RESP = 'Expected json response {}: {}, but got {}'
ERROR_JSON_KEY = 'Expected value "{}" for key "{}" in response, but got value "{}"'
ERROR_TEXT_NOT_IN_RESP = 'Expected the following text "{}" in response: but got {}'
ERROR_TEXT_IN_RESP = 'Did not expect the following text "{}" in response {}: but got {}'
TIMEOUT_MESSAGE = 'Expected {} {}, got {}. Timed out in {} minutes'

MABL_QA_ORG_ID = '5e56dd4a7aba3702d32fee7c'
DR_DEV_ORG_ID_STAGING = '57e43914d75f160c3bac26f6'
DR_DEV_ORG_ID_PROD = '5e4f1fddc3a398004638ca81'

WHAT_IF_APP_ID = '5ce74920a587fd000d4f74de'

LOG_SEPARATOR = '\n' + 120 * '-' + '\n'

# Models
EUCLIDIAN_DISTANCE_MODEL = 'Auto-tuned K-Nearest Neighbors Classifier (Euclidean Distance)'
LOGISTIC_REGRESSION_MODEL = 'Logistic Regression'
DECISION_TREE_CLASSIFIER_MODEL = 'Decision Tree Classifier (Gini)'
NYSTROEM_CLASSIFIER_MODEL = 'Nystroem Kernel SVM Classifier'  # bp19
GENERALIZED_ADDITIVE_MODEL = 'Generalized Additive Model'

OFFICE_DOCUMENT_RESPONSE_HEADER = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

PAYG_FLAGS = {
    FeatureFlags.EXPERIMENTAL_API_ACCESS.value: True,
    FeatureFlags.ENABLE_DATAROBOT_ACCOUNT_PORTAL.value: True,
    FeatureFlags.ENABLE_CREDIT_SYSTEM.value: True,
    # for debugging via UI
    FeatureFlags.ENABLE_PLATFORM_HOME_EXPERIENCE.value: True,
    FeatureFlags.CAN_MANAGE_OWN_PERMISSIONS.value: True,
}
TRIAL_FLAGS = {
    FeatureFlags.EXPERIMENTAL_API_ACCESS.value: True,
    # for debugging via UI
    FeatureFlags.ENABLE_PLATFORM_HOME_EXPERIENCE.value: True,
    FeatureFlags.CAN_MANAGE_OWN_PERMISSIONS.value: True,
}

PAYG_STAGING_PERMISSIONS = {
    FeatureFlags.ALLOW_KUBEWORKERS_JOB_SUBMISSION.value: True,
    FeatureFlags.CAN_CONTACT_SUPPORT.value: False,
    # manually added for easier debugging
    FeatureFlags.CAN_MANAGE_OWN_PERMISSIONS.value: True,
    FeatureFlags.ENABLE_CREDIT_SYSTEM.value: True,
    FeatureFlags.ENABLE_DATAROBOT_ACCOUNT_PORTAL.value: True,
    FeatureFlags.ENABLE_DATASETS_SERVICE_UNDER_EDA_WORKER.value: True,
    FeatureFlags.ENABLE_DEMO_DATASETS.value: True,
    FeatureFlags.ENABLE_DEMO_USE_CASE_SHARING.value: True,
    FeatureFlags.ENABLE_ENHANCED_DATA_INGEST_UX.value: True,
    # added per SELF-2428 due to managed feature rollout
    FeatureFlags.ENABLE_GENERALIZED_SCORING_CODE.value: True,
    FeatureFlags.ENABLE_LIMITED_TEST_PREDICTIONS.value: True,
    FeatureFlags.ENABLE_MLOPS.value: True,
    FeatureFlags.ENABLE_ONBOARDING.value: False,
    FeatureFlags.ENABLE_ONBOARDING_CHECKLIST.value: False,
    FeatureFlags.ENABLE_PENDO_TOURS.value: True,
    # manually added for easier debugging
    FeatureFlags.ENABLE_PLATFORM_HOME_EXPERIENCE.value: True,
    FeatureFlags.ENABLE_PREMIUM_FEATURES_ADVERTISING.value: True,
    FeatureFlags.EXPERIMENTAL_API_ACCESS.value: True,
    FeatureFlags.MANAGED_DEV_FEATURE.value: True,
    FeatureFlags.ENABLE_USER_DEFAULT_WORKERS.value: True,
    FeatureFlags.ENABLE_SESSION_RECORDING.value: False,
    FeatureFlags.ENABLE_ONBOARDING_VIDEOS.value: True,
    FeatureFlags.ENABLE_PUBLIC_API_PREDICTIONS_PROXY.value: True,
    FeatureFlags.ENABLE_SERVERSIDE_BATCHSCORING_SELF_SERVICE.value: True,
    FeatureFlags.ENABLE_TRANSPARENT_PREDICTION_SERVERS.value: True
}
PAYG_APP2_PERMISSIONS = {
    FeatureFlags.CAN_CONTACT_SUPPORT.value: False,
    # manually added for easier debugging
    FeatureFlags.CAN_MANAGE_OWN_PERMISSIONS.value: True,
    FeatureFlags.ENABLE_CREDIT_SYSTEM.value: True,
    FeatureFlags.ENABLE_DATAROBOT_ACCOUNT_PORTAL.value: True,
    FeatureFlags.ENABLE_DATASETS_SERVICE_UNDER_EDA_WORKER.value: True,
    FeatureFlags.ENABLE_DEMO_DATASETS.value: True,
    FeatureFlags.ENABLE_DEMO_USE_CASE_SHARING.value: True,
    FeatureFlags.ENABLE_ENHANCED_DATA_INGEST_UX.value: True,
    # added per SELF-2428 due to managed feature rollout
    FeatureFlags.ENABLE_GENERALIZED_SCORING_CODE.value: True,
    FeatureFlags.ENABLE_LIMITED_TEST_PREDICTIONS.value: True,
    FeatureFlags.ENABLE_MLOPS.value: True,
    FeatureFlags.ENABLE_ONBOARDING.value: False,
    FeatureFlags.ENABLE_ONBOARDING_CHECKLIST.value: False,
    FeatureFlags.ENABLE_PENDO_TOURS.value: True,
    FeatureFlags.ENABLE_PLATFORM_HOME_EXPERIENCE.value: True,
    FeatureFlags.ENABLE_PREMIUM_FEATURES_ADVERTISING.value: True,
    FeatureFlags.EXPERIMENTAL_API_ACCESS.value: True,
    FeatureFlags.ALLOW_KUBEWORKERS_JOB_SUBMISSION.value: True,
}

# Notifications
NF_ERROR_TEXT = 'Expected notification "{}" value {}: {}, but got: {}'
NF_IS_READ = {'isRead': True}
NF_IS_UNREAD = {'isRead': False}
ENABLE_AUTOPILOT_EMAIL_NOTIFICATION = {'settings': {'email_notification': {'on_autopilot_complete': True}}}
NOTIFICATION_EVENT_TYPES = {'eventTypes':
                                ['on_autopilot_complete',
                                 'on_project_shared',
                                 'on_comment_created',
                                 'on_user_mentioned',
                                 'on_model_data_drifting',
                                 'on_model_accuracy_unhealthy',
                                 'on_model_service_unhealthy']}
DEFAULT_USER_NOTIFICATIONS = {'count': 0,
                              'totalCount': 0,
                              'next': None,
                              'data': [],
                              'previous': None}

# Command line args
APP_HOST_ARG = '--app_host'
DR_ACCOUNT_HOST_ARG = '--dr_account_host'
AUTH0_HOST_ARG = '--auth0_host'
REGISTER_DR_ACCOUNT_USER_ARG = '--register_dr_account_user'

# DataRobot Account Portal constants
ADMIN_PERMISSIONS_ERROR = {'error': 'Requires admin permissions'}
PORTAL_ID_OR_EMAIL_REQUIRED_ERROR = 'one of `portalId` and `email` is required'
PORTAL_ID_REQUIRED_ERROR = {'errors': {'portalId': PORTAL_ID_OR_EMAIL_REQUIRED_ERROR,
                                       'email': PORTAL_ID_OR_EMAIL_REQUIRED_ERROR}}
ACCOUNT_NOT_YOURS_ERROR = {'error': 'Cannot access accounts that are not yours.'}
BOTH_PORTAL_ID_AND_EMAIL_ERROR = {'errors': {'email': 'invalid when portalId is provided',
                                             'portalId': 'invalid when email is provided'}}
NOT_VALID_ACCOUNT_ERROR = {'errors': {'portalId': 'not a valid account'}}
EMAIL_NOT_VALID_ACCOUNT_ERROR = {'errors': {'email': 'not a valid account'}}
EXT_SYSTEM_UPDATE_FAIL_ERROR = {'message': 'Portal account update successful; '
                                           'external systems update failed due to missing user'}
PORTAL_ID_ERROR = {'error': 'Invalid portalId claim'}
CANNOT_CONVERT_TO_INT_ERROR = 'value can\'t be converted to int'
CANNOT_CONVERT_TO_FLOAT_ERROR = 'value can\'t be converted to float'
INVALID_EMAIL_ERROR = 'value is not a valid email address'
NOT_STRING_ERROR = 'value is not a string'
PORTAL_ID_INVALID_FORMAT = {'portalId': 'invalid format'}
IS_ADMIN = {'admin': True, 'creditsUser': False}
IS_NOT_ADMIN = {'admin': False, 'creditsUser': False}
METERING_TYPE_FIELDS_DICT = {'str_field': 'test', 'seconds': 12345, 'valid': True}
METERING_NO_CREDIT_USAGE_DETAILS_RESP = {'totalCount': 0, 'data': []}
ID_24_CHARS = '12345678901234567890abcd'
METERING_START_TS_TZ = '2020-08-07T08:00:00Z'
METERING_END_TS_TZ = '2020-08-08T08:00:00Z'
METERING_START_TS_NO_TZ = '2020-08-07T08:00:00+00:00'
METERING_END_TS_NO_TZ = '2020-08-08T08:00:00+00:00'
CREDIT_BALANCE_AFTER_LAST_TRANSACTION = 20000
