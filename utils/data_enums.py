from enum import Enum


class Envs(Enum):
    # app2 hosts
    PROD = 'https://app2.datarobot.com'
    STAGING = 'https://staging.datarobot.com'

    # DataRobot Account Portal hosts
    DR_ACCOUNT_PROD = 'https://id.datarobot.com'
    DR_ACCOUNT_STAGING = 'https://id.staging.infra.ent.datarobot.com'
    DR_ACCOUNT_LOCALHOST = 'http://localhost:5003'

    # Auth0 hosts
    AUTH0_DEV = 'https://datarobotdev.auth0.com'
    AUTH0_PROD = 'https://datarobot.auth0.com'

    # Docs Portal hosts
    DOCS_STAGING = 'https://docs-portal.staging.cloud-native.drdev.io'
    DOCS_PROD = 'http://docs.datarobot.com'


class EnvVars(Enum):
    PENDO_INTEGRATION_KEY = 'PENDO_INTEGRATION_KEY'
    # App2
    ADMIN_API_KEY_STAGING = 'ADMIN_API_KEY_STAGING'
    ADMIN_API_KEY_PROD = 'ADMIN_API_KEY_PROD'

    # DRAP
    # DRAP client id staging
    AUTH0_CLIENT_ID_STAGING = 'AUTH0_CLIENT_ID'
    # DRAP client secret staging
    AUTH0_CLIENT_SECRET_STAGING = 'AUTH0_CLIENT_SECRET'
    # DRAP client id prod
    AUTH0_CLIENT_ID_PROD = 'AUTH0_CLIENT_ID_PROD'
    # DRAP client secret prod
    AUTH0_CLIENT_SECRET_PROD = 'AUTH0_CLIENT_SECRET_PROD'
    DRAP_ADMIN_PASSWORD_PROD = 'DRAP_ADMIN_PASSWORD_PROD'

    # Auth0
    # Auth0 client id staging
    AUTH0_DEV_CLIENT_ID = 'AUTH0_DEV_CLIENT_ID'
    # Auth0 client secret staging
    AUTH0_DEV_CLIENT_SECRET = 'AUTH0_DEV_CLIENT_SECRET'
    # Auth0 client id prod
    AUTH0_PROD_CLIENT_ID = 'AUTH0_PROD_CLIENT_ID'
    # Auth0 client secret prod
    AUTH0_PROD_CLIENT_SECRET = 'AUTH0_PROD_CLIENT_SECRET'


class FeatureFlags(Enum):
    CAN_CONTACT_SUPPORT = 'CAN_CONTACT_SUPPORT'
    CAN_MANAGE_OWN_PERMISSIONS = 'CAN_MANAGE_OWN_PERMISSIONS'
    ENABLE_CREDIT_SYSTEM = 'ENABLE_CREDIT_SYSTEM'
    ENABLE_DATAROBOT_ACCOUNT_PORTAL = 'ENABLE_DATAROBOT_ACCOUNT_PORTAL'
    ENABLE_DATASETS_SERVICE_UNDER_EDA_WORKER =\
        'ENABLE_DATASETS_SERVICE_UNDER_EDA_WORKER'
    ENABLE_DEMO_DATASETS = 'ENABLE_DEMO_DATASETS'
    ENABLE_ENHANCED_DATA_INGEST_UX = 'ENABLE_ENHANCED_DATA_INGEST_UX'
    ENABLE_LIMITED_TEST_PREDICTIONS = 'ENABLE_LIMITED_TEST_PREDICTIONS'
    ENABLE_MLOPS = 'ENABLE_MLOPS'
    ENABLE_PLATFORM_HOME_EXPERIENCE = 'ENABLE_PLATFORM_HOME_EXPERIENCE'
    ENABLE_PREMIUM_FEATURES_ADVERTISING = 'ENABLE_PREMIUM_FEATURES_ADVERTISING'
    ENABLE_SELF_SERVE_AUTOPILOT_SUMMARY = 'ENABLE_SELF_SERVE_AUTOPILOT_SUMMARY'
    ENABLE_PLATFORM_QUESTIONNAIRE = 'ENABLE_PLATFORM_QUESTIONNAIRE'
    ENABLE_MLOPS_WELCOME_SPLASH = 'ENABLE_MLOPS_WELCOME_SPLASH'
    ENABLE_ONBOARDING = 'ENABLE_ONBOARDING'
    ENABLE_ONBOARDING_CHECKLIST = 'ENABLE_ONBOARDING_CHECKLIST'
    ENABLE_ONBOARDING_VIDEOS = 'ENABLE_ONBOARDING_VIDEOS'
    ENABLE_GENERALIZED_SCORING_CODE = 'ENABLE_GENERALIZED_SCORING_CODE'
    MANAGED_DEV_FEATURE = 'MANAGED_DEV_FEATURE'
    EXPERIMENTAL_API_ACCESS = 'EXPERIMENTAL_API_ACCESS'
    ENABLE_NOTIFICATION_CENTER = 'ENABLE_NOTIFICATION_CENTER'
    ENABLE_USER_PUSH_NOTIFICATIONS = 'ENABLE_USER_PUSH_NOTIFICATIONS'
    ENABLE_DEMO_USE_CASE_SHARING = 'ENABLE_DEMO_USE_CASE_SHARING'
    ENABLE_USE_CASE_LIBRARY_SYNC = 'ENABLE_USE_CASE_LIBRARY_SYNC'
    ALLOW_KUBEWORKERS_JOB_SUBMISSION = 'ALLOW_KUBEWORKERS_JOB_SUBMISSION'
    ENABLE_PENDO_TOURS = 'ENABLE_PENDO_TOURS'
    ENABLE_USER_DEFAULT_WORKERS = 'ENABLE_USER_DEFAULT_WORKERS'
    ENABLE_SESSION_RECORDING = 'ENABLE_SESSION_RECORDING'
    ENABLE_PUBLIC_API_PREDICTIONS_PROXY = 'ENABLE_PUBLIC_API_PREDICTIONS_PROXY'
    ENABLE_SERVERSIDE_BATCHSCORING_SELF_SERVICE = 'ENABLE_SERVERSIDE_BATCHSCORING_SELF_SERVICE'
    ENABLE_TRANSPARENT_PREDICTION_SERVERS = 'ENABLE_TRANSPARENT_PREDICTION_SERVERS'


class PagePath(Enum):
    AI_PLATFORM_HOME = '/ai-platform'


class HtmlAttribute(Enum):
    CLASS = 'class'
    HREF = 'href'
    DISABLED = 'disabled'
    VALUE = 'value'
    SRC = 'src'


class UserRole(Enum):
    EXPERIENCED_DS = 'experienced_ds'
    NOVICE_DS = 'novice_ds'
    BUSINESS_ANALYST = 'business_analyst'
    SOFTWARE_DEVELOPER = 'software_developer'
    PRODUCT_MANAGER = 'product_manager'
    DIRECTOR = 'director'
    OTHER = 'other'


class ModelingMode(Enum):
    QUICK = 'quick'
    MANUAL = 'manual'


class ProductUsagePurpose(Enum):
    PREPARE_DATA = 'prepare_data'
    EXPLORE_INSIGHTS = 'explore_insights'
    CREATE_AI_MODELS = 'create_ai_models'
    DEPLOY_AND_MONITOR = 'deploy_and_monitor'


class LearningTrack(Enum):
    PAXATA_DATA_PREP = 'paxata_data_prep'
    ML_DEVELOPMENT = 'ml_development'
    ML_OPERATIONS = 'ml_operations'
    BA = 'business_analyst'


class CreditsSystemDataSource(Enum):
    METERING = 'metering'
    METERING_OVERAGE = 'meteringOverage'
    MANUAL_UPDATE = 'manualUpdate'
    PURCHASE = 'purchase'


class MeteringType(Enum):
    MMJOB = 'mmJob'
    PREDICTIONS = 'prediction'
    DEPLOYMENT = 'deploymentUptime'
    AI_APP = 'aiappUptime'


class CreditsCategory(Enum):
    DATA_PROCESSING = 'Data Processing'
    ML_DEV = 'ML Development'
    ML_OPS = 'MLOps'
    EDA = 'Exploratory Data Analysis'


class ContactSalesCategory(Enum):
    PRICING_INFO = 'Pricing Info'
    MORE_CREDITS = 'Request More Credits'
    GENERAL_INQUIRY = 'General Inquiry'
    LIMIT_INCREASE = 'Request Limit Increase'
    BLUEPRINTS = 'Uncensored Blueprints'


class UserType(Enum):
    TRIAL_USER = 'TrialUser'
    PAYG_USER = 'PayAsYouGoUser'
    PRO_USER = 'ProUser'
    BASIC_USER = 'BasicUser'


class CreditPackType(Enum):
    EXPLORER = 'EXPLORER_PACK'
    ACCELERATOR = 'ACCELERATOR_PACK'


class NfKeys(Enum):
    """GET api/v2/userNotifications/ json keys"""
    DATA = 'data'
    ID = 'data.[].userNotificationId'
    COUNT = 'count'
    TOTAL_COUNT = 'totalCount'
    NEXT = 'next'
    PREVIOUS = 'previous'
    TITLE = 'data.[].title'
    READ = 'data.[].isRead'
    EVENT = 'data.[].eventType'
    PUSH_NF_SENT = 'data.[].pushNotificationSent'
    DESCRIPTION = 'data.[].description'
    LINK = 'data.[].link'


class PredictionServersKeys(Enum):
    """GET api/v2/predictionServers json keys"""
    COUNT = 'count'
    ENDPOINT = 'data.[0].url'
    SERVER_ID = 'data.[0].id'
    DATAROBOT_KEY = 'data.[0].datarobot-key'


class PostApiV2UsersKeys(Enum):
    """POST api/v2/users /"""
    INVITE_LINK = 'notifyStatus.inviteLink'
    USER_ID = 'userId'


class PostJoinKeys(Enum):
    """POST /join"""
    USER_ID = 'profile.id'


class ProjectKeys(Enum):
    """POST /project"""
    ID = 'pid'


class ApiV2ApiKeys(Enum):
    """POST api/v2/account/apiKeys/"""
    KEY = 'key'


class DatasetUploadKeys(Enum):
    """POST /upload/{pid}"""
    UPLOAD_SUCCESS = 'success'


class ProjectStatusKeys(Enum):
    """GET /project/{pid}/status"""
    EDA_STATUS = 'status'


class ModelsKeys(Enum):
    # GET api/v2/{pid}/models/{model_id}
    ID = 'id'
    # GET api/v2/project/{pid}/models/
    TYPE = 'modelType'


class FromLearningModelKeys(Enum):
    """POST api/v2/deployments/fromLearningModel/"""
    DEPLOYMENT_ID = 'id'


class FromRecommendedModelKeys(Enum):
    """POST api/v2/deployments/fromProjectRecommendedModel/"""
    AUTOMODEL_ID = 'id'


class ContactUsKeys(Enum):
    """POST /contactUs"""
    STATUS = 'status'


class DeploymentsKeys(Enum):
    # GET api/v2/deployments/
    FIRST_DEPLOYMENT_ID = 'data.[0].id'
    # GET api/v2/deployments/{deployment_id}
    HAS_AUTOMODEL = 'model.hasAutomodel'
    MODEL_LABEL = 'label'
    DEPLOYMENT_STATUS = 'status'
    ID = 'id'


class DeploymentActionLogKeys(Enum):
    """GET api/v2/modelDeployments/{deployment_id}/actionLog"""
    COUNT = 'count'


class AppsKeys(Enum):
    """POST api/v2/applications/"""
    DEPLOYMENT_STATE = 'deploymentState'
    ID = 'id'


class ServiceStatsKeys(Enum):
    """GET api/v2/deployments/{deployment_id}/serviceStats/"""
    PREDICTION_ROWS = 'metrics.totalPredictions'


class ModelValidationKeys(Enum):
    """POST api/v2/deployments/{deployment_id}/model/validation/"""
    MESSAGE = 'message'


class AccountLoginKeys(Enum):
    """POST /account/login"""
    UID = 'uid'


class GetProfileKeys(Enum):
    """GET /api/profile"""
    INDUSTRY = 'industry'
    LEARNING_TRACK = 'selected_learning_track'
    USER_ROLE = 'user_role'
    USAGE_PURPOSE = 'product_usage_purpose'
    WELCOME_VIDEO_VIEWED = 'welcome_video_viewed'
    PERMISSIONS = 'permissions'
    MAX_APP_COUNT = 'max_app_count'
    MAX_EDA_WORKERS = 'max_eda_workers'
    MAX_RAM_CONSTRAINTS = 'max_ram_constraints'
    GROUP_LIMIT = 'group_limit'
    MAX_UPLOAD_SIZE = 'max_upload_size'
    MAX_WORKERS = 'max_workers'


class RecommendedModelsKeys(Enum):
    """GET /projects/{project_id}/recommendedModels/"""
    RECOMMENDED_MODEL = '[0].modelId'


class CommentsKeys(Enum):
    """POST api/v2/comments/"""
    ID = 'id'


class DatasetsDatasetIdKeys(Enum):
    # GET api/v2/datasets/{dataset_id}/
    ID = 'datasetId'
    STATE = 'processingState'


class DrapProfileKeys(Enum):
    """GET api/account/profile"""
    NAME = 'firstName'
    LAST_NAME = 'lastName'


class DrapRegisterUserKeys(Enum):
    """POST api/admin/registerUser"""
    PORTAL_ID = 'portalId'


class BalanceSummaryKeys(Enum):
    """
    GET api/creditsSystem/creditBalanceSummary?email=email
    GET /api/creditsSystem/creditBalanceSummary
    """
    LAST_TRANSACTION_DATE = 'lastCreditTransactionDate'
    BALANCE_AFTER_LAST_TRANSACTION = 'balanceAfterLastCreditTransaction'
    CURRENT_BALANCE = 'currentBalance'
    RAW_BALANCE = 'currentBalanceRaw'


class CreditUsageDetailsKeys(Enum):
    """GET api/creditsSystem/creditUsageDetails"""
    TOTAL_COUNT = 'totalCount'
    DATA = 'data'


class CreditPackKeys(Enum):
    # POST api/billing/createCheckout
    CLIENT_REF_ID = 'clientReferenceId'
    CHECKOUT_SESSION_ID = 'checkoutSessionId'
    # POST api/admin/creditsSystem/registerCreditPurchase
    RECORD_ID = 'recordId'


class CreateInvoiceKeys(Enum):
    # GET api/v2/billing/createInvoice/
    INVOICE_ID = 'invoiceId'
    INVOICE_URL = 'invoiceUrl'


class CreditUsageSummaryKeys(Enum):
    """GET api/v2/creditsSystem/creditUsageSummary/"""
    DATA = 'data'
    KEY = 'key'


class AiAppUptimeKeys(Enum):
    """GET api/v2/admin/metering/aiappUptime/activity/"""
    APP_TYPE_ID = 'data.[0].applicationTypeId'
    UPTIME = 'data.[0].uptimeSeconds'
    PID = 'data.[0].projectId'
    USER_ID = 'data.[0].userId'
    DEPLOYMENT_ID = 'data.[0].deploymentId'
    APP_ID = 'data.[0].appId'


class DeploymentUptimeKeys(Enum):
    """GET api/v2/admin/metering/deploymentUptime/activity/"""
    UPTIME = 'data.[0].uptimeSeconds'
    PID = 'data.[0].projectId'
    USER_ID = 'data.[0].userId'
    DEPLOYMENT_ID = 'data.[0].deploymentId'
    DEPLOYMENT_TYPE = 'data.[0].deploymentType'


class PredictionUptimeKeys(Enum):
    """GET api/v2/admin/metering/prediction/activity/"""
    EXEC_TIME = 'data.[0].executionTimeMilliseconds'
    PID = 'data.[0].projectId'
    USER_ID = 'data.[0].userId'
    DEPLOYMENT_ID = 'data.[0].deploymentId'


class Auth0Keys(Enum):
    # GET api/v2/users-by-email?email=email@test.com
    USER_ID = '[0].user_id'
    PORTAL_ID = '[0].app_metadata.portal_id'
    ACCESS_TOKEN = 'access_token'
