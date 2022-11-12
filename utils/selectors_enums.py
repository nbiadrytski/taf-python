from enum import Enum

from utils.ui_constants import PENDO_HIGHLIGHT


TEST_ID = 'css=[test-id={}]'
TEXT = 'text={}'
TEST_ID_TEXT_IS = 'css=[test-id={}] :text-is("{}")'
TOOLTIP_TEXT_CLASS_VALUE = 'div.bb-text._pendo-text-paragraph'


class PendoTourSelectors(Enum):
    TOUR_CONTAINER = '#pendo-guide-container'
    NO_THANKS_BUTTON = TEXT.format('No thanks')
    REMIND_ME_TOMORROW_BUTTON = TEXT.format('Remind me tomorrow')
    CLOSE_TOUR_X_BUTTON = 'css=[aria-label="Close"]'
    START_TOUR_BUTTON = 'button:has-text("Start tour")'
    # Start Home tour with Show me around first button
    SHOW_ME_AROUND_BUTTON = TEXT.format('Show me around first')
    BACK_BUTTON = 'button:has-text("Back")'
    NEXT_BUTTON = 'button:has-text("Next")'
    HELPFUL_NO_BUTTON = 'button:has-text("No")'
    HELPFUL_YES_BUTTON = 'button:has-text("Yes")'
    TOUR_START_PAGE_IMAGE = '#image0'
    WAS_TOUR_HELPFUL_TEXT = TEXT.format('Was this tour helpful?')


class ToursGuideSelectors(Enum):
    ROBOT_ICON = 'css=[data-layout=badgeResourceCenter]'
    ROBOT_ICON_NOTIFICATION_COUNT = 'div.pendo-notification-bubble-unread-count'
    EXPLORE_DATAROBOT_GUIDE_HEADER = TEXT.format('Explore DataRobot')
    # Both Tour Guide menu option and 'back' button to return from ANNOUNCEMENTS to Tour Guide
    ANNOUNCEMENTS = TEXT.format('Announcements')
    ANNOUNCEMENT_COUNT = 'div._pendo-home-view-bubble'
    LEFT_ARROW_BUTTON = 'div._pendo-resource-center-left-caret'
    # :has-text("{}") --> is content itself
    ANNOUNCEMENT_CONTENT = '#pendo-guide-container >> :has-text("{}") >> ' \
                           ':has-text("Launch Tour")'
    LAUNCH_TOUR_BUTTON = TEXT.format('Launch Tour')
    ONBOARDING_TOURS = TEXT.format('Onboarding Tours')
    PROGRESS_BAR = '#pendo-progress-bar-e96cc0f3'
    TOUR_ROW = 'div._pendo-row._pendo-resource-center-onboarding-module-guide-row'
    BUILD_AI_MODELS_TOUR = f'{TOUR_ROW} :has-text("Build AI Models")'


class HomePageSelectors(Enum):
    HOME_PAGE_TITLE = TEXT.format('AI Platform Home')
    BUY_CREDITS = TEST_ID.format('buy-more-credits')
    # 1st param is either ML_DEV_CARD or ML_OPS_CARD or PAXATA_DATA_PREP_CARD
    RECOMMENDED_LABEL = '{} >> span.highlighted-badge.uppercased-text.success.recommended-badge' \
                        ' >> text=Recommended'
    LEARNING_TRACK_CONTAINER = 'div.card-container'
    LEARNING_TRACK_STEPS = f'{LEARNING_TRACK_CONTAINER} >> [test-id="embedded-steps"] >> div.embedded-step-marker'
    # ML Dev Learning Track
    ML_DEV_TRACK = f'{LEARNING_TRACK_CONTAINER} >> [test-id="checklist-ml_development"]'
    ML_DEV_TRACK_HEADER = f'{ML_DEV_TRACK} >> div.header-container'
    ML_DEV_TRACK_TITLE = f'{ML_DEV_TRACK_HEADER} >> :has-text("Data Science Learning Track")'
    ML_DEV_TRACK_ROBOT_ICON = f'{ML_DEV_TRACK_HEADER} >> [test-id="datarobot-icon"]'
    ML_DEV_CONTINUE_BUTTON = TEST_ID.format('checklist-ml_development-continue-button')
    ML_DEV_TRACK_DESCRIPTION = f'{LEARNING_TRACK_CONTAINER}' \
                               f' >> :has-text("Learn the basics of ML Development by following these simple steps.")'
    DOT_TEXT = 'span.dot-text'
    ML_DEV_SELECT_USE_CASE_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT}.active >> text=Select Use Case'
    ML_DEV_SET_TARGET_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Set Target'
    ML_DEV_EXPLORE_DATA_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Explore Data'
    ML_DEV_COMPARE_MODELS_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Compare Models'
    ML_DEV_CREATE_DEPLOY_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Create Deployment'
    ML_DEV_PREDICTIONS_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Make Predictions'
    ML_DEV_AI_APP_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Launch AI App'
    # ML Dev card
    ML_DEV_CARD = TEST_ID.format('ml_development')
    ML_DEV_CARD_ICON = f'{ML_DEV_CARD} >> svg >> g >> #icons_platform'
    ML_DEV_CARD_TITLE = f'{ML_DEV_CARD} >> p.small-header >> text=ML Development'
    ML_DEV_CARD_DESCRIPTION = f'{ML_DEV_CARD} >> p.small-subtext >> ' \
                              f'text=Use AutoML, Visual AI, and more to build machine learning models in minutes.'
    # Data Preparation Learning Track
    DATA_PREP_TRACK = f'{LEARNING_TRACK_CONTAINER} >> [test-id="checklist-paxata_data_prep"]'
    DATA_PREP_TRACK_HEADER = f'{DATA_PREP_TRACK} >> div.header-container'
    DATA_PREP_TRACK_TITLE = f'{DATA_PREP_TRACK} >> :has-text("Introduction to DataRobot Data Prep")'
    DATA_PREP_TRACK_ROBOT_ICON = f'{DATA_PREP_TRACK} >> [test-id="datarobot-icon"]'
    DATA_PREP_CONTINUE_BUTTON = TEST_ID.format('checklist-paxata_data_prep-continue-button')
    DATA_PREP_TRACK_DESCRIPTION = f'{LEARNING_TRACK_CONTAINER} >> :has-text(' \
                                  f'"Learn how to create a Learning dataset, or to make your existing data AI-ready.")'
    DATA_PREP_SELECT_DATA_SOURCE_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT}.active >> text=Select Data Source'
    DATA_PREP_COMBINE_ENRICH_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Combine and Enrich'
    DATA_PREP_CLEANUP_DATA_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Cleanup Data'
    DATA_PREP_TARGET_VAR_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Define Target Variable'
    DATA_PREP_EXPORT_TO_ML_DEV_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Export to ML Dev'
    # Data Preparation card
    PAXATA_DATA_PREP_CARD = TEST_ID.format('paxata_data_prep')
    DATA_PREP_CARD_ICON = f'{PAXATA_DATA_PREP_CARD} >> svg >> path'
    DATA_PREP_CARD_TITLE = f'{PAXATA_DATA_PREP_CARD} >> p.small-header >> text=Data Preparation'
    DATA_PREP_CARD_DESCRIPTION = f'{PAXATA_DATA_PREP_CARD} >> p.small-subtext >> text=' \
                                 f'Use DataRobot Data Prep to visually prepare datasets, making them ready for machine learning.'
    # ML Ops Learning Track
    ML_OPS_TRACK = f'{LEARNING_TRACK_CONTAINER} >> [test-id="checklist-ml_operations"]'
    ML_OPS_TRACK_HEADER = f'{ML_OPS_TRACK} >> div.header-container'
    ML_OPS_TRACK_TITLE = f'{ML_OPS_TRACK} >> :has-text("Introduction to MLOps")'
    ML_OPS_TRACK_ROBOT_ICON = f'{ML_OPS_TRACK} >> [test-id="datarobot-icon"]'
    ML_OPS_CONTINUE_BUTTON = TEST_ID.format('checklist-ml_operations-continue-button')
    ML_OPS_TRACK_DESCRIPTION = f'{LEARNING_TRACK_CONTAINER} >> :has-text(' \
                               f'"Explore sample deployments, configure monitoring, quickly deploy your model.")'
    ML_OPS_CREATE_DEPLOY_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT}.active >> text=Create Deployment'
    ML_OPS_PREDICTIONS_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Make Predictions'
    ML_OPS_AI_APP_STEP = f'{LEARNING_TRACK_STEPS} >> {DOT_TEXT} >> text=Launch AI App'
    # ML Ops card
    ML_OPS_CARD = TEST_ID.format('ml_operations')
    ML_OPS_CARD_ICON = f'{ML_OPS_CARD} >> svg >> path'
    ML_OPS_CARD_TITLE = f'{ML_OPS_CARD} >> p.small-header >> text=ML Operations'
    ML_OPS_CARD_DESCRIPTION = f'{ML_OPS_CARD} >> p.small-subtext >> text=' \
                              f'Use MLOps to deploy, monitor, and manage machine learning models in production.'
    # Recent Projects section (ML Dev track)
    RECENT_PROJECTS_TITLE = f'{LEARNING_TRACK_CONTAINER} >> [test-id="home-page-recent-projects"]' \
                            f' :has-text("Recent Projects")'
    CREATE_NEW_PROJECT_BUTTON = TEST_ID.format('create-new-project')
    RECENT_PROJECTS_TABLE = f'{LEARNING_TRACK_CONTAINER} >> [test-id="project-management-table-react"]'
    RECENT_PROJECTS_COLUMN = f'{RECENT_PROJECTS_TABLE} >> [test-id="sortable-table-r-th"]'
    RECENT_PROJECTS_PROJECT_NAME_COLUMN = f'{RECENT_PROJECTS_TABLE} >> [test-id="project-name-header"]' \
                                          f' :has-text("Project Name")'
    RECENT_PROJECTS_DATASET_COLUMN = f'{RECENT_PROJECTS_COLUMN} :has-text("Dataset")'
    RECENT_PROJECTS_MODEL_TYPE_COLUMN = f'{RECENT_PROJECTS_COLUMN} :has-text("Model type")'
    RECENT_PROJECTS_TARGET_COLUMN = f'{RECENT_PROJECTS_COLUMN} :has-text("Target")'
    RECENT_PROJECTS_PROJECT_NAME = f'{RECENT_PROJECTS_TABLE} >> div.project-name-container' \
                                   f' :has-text("10k_diabetes.csv")'
    RECENT_PROJECTS_DATASET_NAME = f'{RECENT_PROJECTS_TABLE} >> div.r-td.file-name-cell' \
                                   f' :has-text("10k_diabetes.csv")'
    # Recent Deployments section (ML Ops track)
    RECENT_DEPLOYMENTS_HEADER = f'{LEARNING_TRACK_CONTAINER} >> div.recent-data'
    RECENT_DEPLOYMENTS_TITLE = f'{RECENT_DEPLOYMENTS_HEADER} :has-text("Recent Deployments")'
    GO_TO_MLOPS_BUTTON = f'{RECENT_DEPLOYMENTS_HEADER} >> [test-id="go-to-mlops"]'
    RECENT_DEPLOYMENTS_TABLE = f'{LEARNING_TRACK_CONTAINER} >> div.r-table.deployments-table'
    RECENT_DEPLOYMENTS_TABLE_COLUMNS_NAMES = f'{RECENT_DEPLOYMENTS_TABLE} >> div.r-thead'
    RECENT_DEPLOYMENTS_TABLE_CONTENT = f'{RECENT_DEPLOYMENTS_TABLE} >> div.r-tbody'
    RECENT_DEPLOYMENTS_DEPLOYMENT_NAME_COLUMN = f'{RECENT_DEPLOYMENTS_TABLE_COLUMNS_NAMES} ' \
                                                f':has-text("Deployment Name")'
    RECENT_DEPLOYMENTS_ACTIVITY_COLUMN = f'{RECENT_DEPLOYMENTS_TABLE_COLUMNS_NAMES} ' \
                                         f':has-text("Activity")'
    RECENT_DEPLOYMENTS_PREDICTION_COLUMN = f'{RECENT_DEPLOYMENTS_TABLE_COLUMNS_NAMES} ' \
                                           f':has-text("Last Prediction")'
    RECENT_DEPLOYMENTS_DEPLOYMENT_NAME = f'{RECENT_DEPLOYMENTS_TABLE_CONTENT} >> [test-id="deployment-name"]'
    RECENT_DEPLOYMENTS_PREDICTION_SERVER = f'{RECENT_DEPLOYMENTS_TABLE_CONTENT} >> [test-id="deployment-location-and-project"]'
    # RECENT_DEPLOYMENTS_DEPLOYMENT_PROJECT = f'{RECENT_DEPLOYMENTS_TABLE_CONTENT} >> [test-id="deployment-project"]'
    RECENT_DEPLOYMENTS_ACTIVITY_GRAPH = f'{RECENT_DEPLOYMENTS_TABLE_CONTENT} >> ' \
                                        f'div.r-td.activity-column >> ' \
                                        f'div.request-histogram.graph-container :has-text("now")'
    RECENT_DEPLOYMENTS_LAST_PREDICTION = f'{RECENT_DEPLOYMENTS_TABLE_CONTENT} >> ' \
                                         f'span.last-prediction-column-cell :has-text("—")'
    CREDITS_OVERVIEW_LINE = TEST_ID.format('credits-overview')
    YOU_HAVE_N_CREDITS = TEST_ID.format('credits-balance')
    CREDITS_OVERVIEW_LINE_VALUE = 'css=[test-id=credits-overview] :has-text("{}")'
    CREDITS_USAGE_DROPDOWN_BUTTON = TEST_ID.format('credits-dropdown-button')
    CREDITS_USAGE_DROPDOWN_BUTTON_VALUE = 'css=[test-id=credits-dropdown-button] :has-text("{}")'
    CREDIT_USAGE_WIDGET = TEST_ID.format('credit-usage-widget')
    WIDGET_CIRCLE = 'div.circle-progress'
    NO_CREDITS_USED_YET_TEXT = f'{CREDIT_USAGE_WIDGET} ' \
                               f':has-text("It looks like you haven\'t used any credits for that period yet")'
    FULL_USAGE_DETAILS_LINK = TEXT.format('Full Usage Details')
    WIDGET_DROPDOWN_MENU = 'button.dropdown-trigger.dropdown-menu-trigger'
    WIDGET_DATE_DROPDOWN = f'{WIDGET_DROPDOWN_MENU} :has-text("Date:")'
    WIDGET_USAGE_DROPDOWN = f'{WIDGET_DROPDOWN_MENU} :has-text("Usage:")'
    WIDGET_DATE_DROPDOWN_SELECTED_FILTER = 'button.dropdown-trigger.dropdown-menu-trigger ' \
                                           'span.selected-item :has-text("Last {} days")'
    WIDGET_USAGE_DROPDOWN_SELECTED_FILTER = 'button.dropdown-trigger.dropdown-menu-trigger ' \
                                            'span.selected-item :has-text("By {}")'
    LAST_N_DAYS_DROPDOWN_OPTION = 'li.drop-item :has-text("Last {} days")'
    WIDGET_USAGE_DROPDOWN_OPTION = 'li.drop-item :has-text("By {}")'
    USAGE_CATEGORY = 'div.usage-list dl.usage-row.small-subtext dd :has-text("{}")'
    USAGE_DROPDOWN_CATEGORIES_LIST = 'div.usage-list'


EXPLORER_PRODUCT_ID_STAGING = 'prod_IUexvR3CTuX9Vg'
EXPLORER_PRODUCT_ID_PROD = 'prod_IUMpGwmDGSOvD5'
ACCEL_PRODUCT_ID_STAGING = 'prod_IUezulxOGLMKp8'
ACCEL_PRODUCT_ID_PROD = 'prod_IUMqdlGgbZGUf7'


class CreditsPacksPageSelectors(Enum):
    BUY_EXPLORER_PACK_BUTTON = TEST_ID.format('buy-explorer-pack-button')
    BUY_ACCEL_PACK_BUTTON = TEST_ID.format('buy-accel-pack-button')
    PACK_CARD_BACK_SIDE = 'div.card-container.card-border.flip-content'
    PROCEED_BUTTON = f'{PACK_CARD_BACK_SIDE} button.buy-now-button.primary'
    CONTACT_SALES_BUTTON = TEST_ID.format('contact-sales-button')
    CONTACT_SALES_MODAL = 'css=[data-testid=feedback-modal]'
    PACKS_CONTENT = 'div.credits-content'
    EXPLORER_CARD_IMAGE = f'{PACKS_CONTENT} ' \
                          f'>> div:nth-child(1) >> img.card-icon'
    ACCEL_CARD_IMAGE = f'{PACKS_CONTENT} >> div:nth-child(2) >> img.card-icon'
    # Country drop-down
    EXPLORER_COUNTRY_DROPDOWN_STAGING = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_STAGING}-country-dropdown')
    EXPLORER_COUNTRY_DROPDOWN_PROD = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_PROD}-country-dropdown')
    ACCEL_COUNTRY_DROPDOWN_STAGING = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_STAGING}-country-dropdown')
    ACCEL_COUNTRY_DROPDOWN_PROD = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_PROD}-country-dropdown')
    # Street address field
    EXPLORER_STREET_ADDRESS_FIELD_STAGING = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_STAGING}-street-address-input')
    EXPLORER_STREET_ADDRESS_FIELD_PROD = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_PROD}-street-address-input')
    ACCEL_STREET_ADDRESS_FIELD_STAGING = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_STAGING}-street-address-input')
    ACCEL_STREET_ADDRESS_FIELD_PROD = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_PROD}-street-address-input')
    # City field
    EXPLORER_CITY_FIELD_STAGING = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_STAGING}-city-input')
    EXPLORER_CITY_FIELD_PROD = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_PROD}-city-input')
    ACCEL_CITY_FIELD_STAGING = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_STAGING}-city-input')
    ACCEL_CITY_FIELD_PROD = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_PROD}-city-input')
    # State drop-down
    EXPLORER_STATE_DROPDOWN_STAGING = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_STAGING}-state-dropdown')
    EXPLORER_STATE_ADDRESS_FIELD_PROD = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_PROD}-state-dropdown')
    ACCEL_STATE_DROPDOWN_STAGING = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_STAGING}-state-dropdown')
    ACCEL_STATE_ADDRESS_FIELD_PROD = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_PROD}-state-dropdown')
    # Zip code field
    EXPLORER_ZIP_FIELD_STAGING = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_STAGING}-zip-code-input')
    EXPLORER_ZIP_FIELD_PROD = TEST_ID.format(
        f'{EXPLORER_PRODUCT_ID_PROD}-zip-code-input')
    ACCEL_ZIP_FIELD_STAGING = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_STAGING}-zip-code-input')
    ACCEL_ZIP_FIELD_PROD = TEST_ID.format(
        f'{ACCEL_PRODUCT_ID_PROD}-zip-code-input')


class InvoiceCardPageSelectors(Enum):
    VIEW_INVOICE_DETAILS_BUTTON = TEXT.format('View invoice details')
    CLOSE_INVOICE_DETAILS_FROM_CARD_BUTTON = TEXT.format('Close invoice details')
    CLOSE_INVOICE_DETAILS_X_BUTTON = 'button.Button.CloseDrawerButton.Button--link.Button--md'
    INVOICE_DETAILS_CONTENT = 'div.Drawer-content'
    INVOICE_DETAILS_CONTACT_DR_BUTTON = 'button.Button.Button--link.Button--md :has-text("Contact DataRobot")'
    INVOICE_DETAILS_CONTACT_DR_POPOVER = 'div.ContextualPopover'
    INVOICE_DETAILS_CONTACT_DR_POPOVER_EMAIL = f'{INVOICE_DETAILS_CONTACT_DR_POPOVER} ' \
                                               f':has-text("trial-support@datarobot.com")'
    INVOICE_DETAILS_CONTACT_DR_POPOVER_PHONE = f'{INVOICE_DETAILS_CONTACT_DR_POPOVER} ' \
                                               f':has-text("+16177654500")'
    CARD_PRICE = 'div.ContentCard :text-is("{}")'
    CARD_DATE = 'div.ContentCard :has-text("{}")'
    CARD_FIRST_LAST_NAME = 'table.InvoiceDetails-table :has-text("{} {}")'
    CARD_FROM = 'table.InvoiceDetails-table :has-text("DataRobot")'
    CARD_INVOICE_DOWNLOAD_ICON = 'button.InvoiceThumbnail-wrapperButton'
    CARD_INVOICE_DOWNLOAD_BUTTON = 'button.InvoiceThumbnail-downloadButton'
    CARD_NUMBER_FIELD = '#cardNumber'
    CARD_EXPIRY_FIELD = '#cardExpiry'
    CARD_CVC_FIELD = '#cardCvc'
    PAY_PRICE_BUTTON = 'div.SubmitButton-TextContainer :has-text("{}")'
    INVOICE_PAID_TEXT = TEXT.format('Invoice paid')
    PAID_INVOICE_CARD_THUMBNAIL = 'div.InvoiceThumbnail'
    PAID_INVOICE_CARD_THUMBNAIL_SUCCESS_ICON = 'div.InvoiceThumbnail-successMark'
    PAID_INVOICE_CARD_TABLE = 'table.InvoiceDetails-table :has-text("{}")'
    DOWNLOAD_PAID_INVOICE_BUTTON = 'button.Button.Button--primary.Button--md :has-text("Download invoice")'
    DOWNLOAD_RECEIPT_BUTTON = 'button.Button.Button--primary.Button--md :has-text("Download receipt")'
    PAID_INVOICE_DETAILS_INVOICE_NUMBER = 'text=Invoice #{}'


class SignInPageSelectors(Enum):
    APP2_EMAIL_FIELD = '#email'
    STAGING_EMAIL_FIELD = '#signInInputUsername'
    APP2_PASSWORD_FIELD = '#password'
    STAGING_PASSWORD_FIELD = '#signInInputPassword'
    APP2_SIGN_IN_BUTTON = '#btn-login'
    APP2_GOOGLE_SIGN_IN_BUTTON = '#btn-google-text'
    # The below is also CONTINUE button at pre-sign in page
    STAGING_SIGN_IN_BUTTON = TEST_ID.format('login-button')


class NewPageSelectors(Enum):
    HDFS_BUTTON = TEST_ID.format('project-create-button-hdfs')
    DEMO_DATASETS_LIST = TEST_ID.format('demo-dataset-cards')
    AI_CATALOG_BUTTON = TEST_ID.format('create-from-catalog-button')
    HOSPITAL_READMISSION_DEMO_DATASET = TEST_ID.format('demo-dataset_0')
    PREDICT_LATE_SHIPMENT_DEMO_DATASET = TEST_ID.format('demo-dataset_2')
    WELCOME_SPLASH_MODAL_FIRST_SLIDE_HEADER = TEST_ID.format(
        'ai-platform-trial-first-slide-header')
    WELCOME_SPLASH_MODAL_CLOSE_BUTTON = TEST_ID.format('close-button')
    IMPORT_DATASET_BUTTON = TEST_ID.format('import-dataset')
    PREDICT_LATE_SHIPMENT_DEMO_DATASET_IMPORT_BUTTON =\
        f'{PREDICT_LATE_SHIPMENT_DEMO_DATASET} div.more-info' \
        f' :has-text("Import dataset")'
    DATASETS_REQUIREMENTS = TEXT.format(
        'Datasets containing sensitive personal data including health data,'
        '\n\n\n\n\n\n\n\n\n\n\n\n\nfinancial data, and data related to minors,'
        ' are prohibited.')
    DATASETS_REQUIREMENTS_BUTTON = TEST_ID.format(
        'trial-user-dataset-requirements-button')
    DATASETS_REQUIREMENTS_MODAL_TITLE = TEXT.format(
        'DataRobot Trial Dataset Requirements')
    DATASETS_REQUIREMENTS_MODAL_LEARN_MORE_BUTTON =\
        f'footer.dr-modal-footer >> div >> a.anchor.button.secondary' \
        f' :has-text("Learn more")'
    DATASETS_REQUIREMENTS_MODAL_CLOSE_BUTTON =\
        'css=[test-id="dr-modal-header"] >> css=[test-id="close-button"]'
    DATASETS_REQUIREMENTS_MODAL_GOT_IT_BUTTON = TEST_ID.format('i-am-going')


class DataPageSelectors(Enum):
    # Recommended target is: {RECOMMENDED_TARGET_BUTTON}
    RECOMMENDED_TARGET_BUTTON = TEST_ID.format('recommended-target')
    ENTERED_TARGET = TEST_ID.format('target-feature-select')
    SELECTED_MODELING_MODE = TEST_ID.format('selected-modeling-mode')
    START_MODELING_BUTTON = TEST_ID.format('start-project-button')
    SETTING_TARGET_FEATURE_EDA_STEP = TEXT.format('Setting target feature')
    SELECT_TARGET_BUTTON_RIGHT_SIDEBAR = TEST_ID.format('select-target-continue')
    EXPLORE_DATA_BUTTON = TEST_ID.format('explore-data')
    DATA_QUALITY_INFO_BUTTON = TEST_ID.format('data-quality-info-button')
    DATA_QUALITY_VIEW_INFO_BUTTON = f'{DATA_QUALITY_INFO_BUTTON} :has-text("View info")'
    DATA_QUALITY_CLOSE_INFO_BUTTON = f'{DATA_QUALITY_INFO_BUTTON} :has-text("Close info")'
    VENDOR_FEATURE = TEST_ID.format('Vendor')
    SELECT_TARGET_SECTION_PENDO_HIGHLIGHTED = f'[test-id="recommended-target"] >> span.{PENDO_HIGHLIGHT}'


class ModelsPageSelectors(Enum):
    # Models
    RANDOM_FOREST_CLASSIFIER_GINI_MODEL = TEST_ID_TEXT_IS.format(
        'expand-model', 'RandomForest Classifier (Gini)')
    GRADIENT_BOOSTED_TREES_CLASSIFIER_MODEL = TEST_ID_TEXT_IS.format(
        'expand-model', 'Gradient Boosted Trees Classifier')

    MODEL_DETAILS_PREDICT_TAB = TEST_ID.format('predict-tab')
    MODEL_DETAILS_DEPLOY_TAB = TEST_ID.format('expanded-leaderboard-menu-tab-deploy')
    DEPLOY_MODEL_BUTTON = TEST_ID.format('create-deployment-button')
    AUTOMODEL_BUTTON = TEST_ID.format('deploy-recommended-model')
    AUTOMODEL_DEPLOYED_BUTTON = TEST_ID.format('link-to-automodel-deployment')
    WELCOME_VIDEO = TEST_ID.format('embedded-video')
    WELCOME_VIDEO_CLOSE_BUTTON = TEST_ID.format('close-button')


class DeploymentsPageSelectors(Enum):
    # Create deployment button at
    # deployments/new/configure?packageId={package_id}
    CREATE_DEPLOYMENT_BUTTON = TEST_ID.format('save-deployment-button')
    # Create deployment button at Review Deployment Importance modal
    REVIEW_MODAL_CREATE_DEPLOYMENT_BUTTON = TEST_ID_TEXT_IS.format('modal-close', 'Create deployment')
    # At deployments/{deployment_id}/overview page
    DEPLOYMENT_CREATED_TILE = TEST_ID_TEXT_IS.format('deployment-governance-tile-no-content', 'Deployment Created')
    AUTOMODEL_DEPLOYED_FLAG = TEST_ID.format('deployment-automodel-flag')
    DEPLOYMENT_ACTIONS_MENU = TEST_ID.format('deployment-actions-menu-trigger')
    DELETE_DEPLOYMENT_BUTTON = TEST_ID.format('delete-deployment')
    CREATE_APP_BUTTON = TEST_ID.format('deploy-apps')
    DEPLOY_APP_BUTTON = TEST_ID.format('deploy-app')
    WHAT_IF_APP = TEST_ID.format('What-If')
    # DEPLOYMENT PREDICTION TAB
    PREDICTIONS_TAB = TEST_ID.format('deployment-predictions-link')
    DOWNLOAD_SAMPLE_DATA_BUTTON = TEST_ID.format('demo-prediction-dataset-download')
    CHOOSE_PREDICTION_FILE_BUTTON = TEST_ID.format('file-uploader-dropdown-menu-trigger')
    UPLOAD_SAMPLE_DATA_FILE_INPUT = TEST_ID.format('drop-file-upload-input-upload-local-file')
    COMPUTE_DOWNLOAD_PREDICTIONS_BUTTON = TEST_ID.format('make-predictions-submit-button')
    # A small icon at predictions card which appears when predictions have been computed
    DOWNLOAD_FINISHED_PREDICTIONS_BUTTON = TEST_ID.format('completed-prediction-job-download-button')
    # You have exceeded your limit on total modeling API requests. Try again in 6 seconds.
    PREDICTIONS_ERROR_ALERT = TEST_ID.format('make-predictions-error')
    # MLOPS SPLASH MODAL
    SPLASH_MODAL_WELCOME_PAGE = TEST_ID.format('welcome-splash-modal-container')
    # MLOps splash modal close X button (top right corner)
    SPLASH_MODAL_CLOSE_BUTTON = TEST_ID.format('close-button')
    ACTIVE_DEPLOYMENTS_COUNT = TEST_ID.format('deployment-count-summary')


class AppsPageSelectors(Enum):
    OPEN_APP_BUTTON = TEST_ID.format('open-app')
    APP_DETAILS_BUTTON = 'css=[tour-id=app-details-button]'


class WhatIfAppPageSelectors(Enum):
    MANAGE_VARIABLES_TEXT = TEXT.format('Manage variables')


class ModelingRightSidebar(Enum):
    REMOVE_TASKS_BUTTON = TEST_ID.format('queue-remove-all-button')


class AiProfilePageSelectors(Enum):
    TELL_ABOUT_YOURSELF_TEXT = TEXT.format('Tell us a little about yourself')
    HOW_DR_CAN_HELP_TEXT = TEXT.format('How can DataRobot help you?')
    ROLE_DROPDOWN = TEST_ID.format('role-dropdown')
    INDUSTRY_DROPDOWN = TEST_ID.format('industry-dropdown')
    NEXT_BUTTON = TEST_ID.format('next-question')
    START_BUTTON = TEST_ID.format('save-info-button')
    # Roles
    ANALYST = TEXT.format('Analyst')
    DATA_SCIENTIST = TEXT.format('Data scientist')
    DEVELOPER = TEXT.format('Developer')
    DIRECTOR = TEXT.format('Director')
    EXECUTIVE = TEXT.format('Executive')
    PRODUCT_MANAGER = TEXT.format('Product manager')
    OTHER = TEXT.format('Other')
    # Industries
    AIRLINES = TEXT.format('Airlines')
    AUTOMOTIVE = TEXT.format('Automotive')
    FINANCE = TEXT.format('Financial services')
    GAMING = TEXT.format('Gaming')
    HEALTHCARE = TEXT.format('Healthcare')
    EDUCATION = TEXT.format('Higher education')
    INSURANCE = TEXT.format('Insurance')
    MANUFACTURING = TEXT.format('Manufacturing')
    MEDIA = TEXT.format('Media')
    NON_PROFIT = TEXT.format('Non profit')
    RETAIL = TEXT.format('Retail')
    SPORTS = TEXT.format('Sports')
    TECH = TEXT.format('Technology')
    TELECOM = TEXT.format('Telecom')
    # Tracks
    PREPARE_DATA = TEST_ID.format('prepare_data')
    EXPLORE_INSIGHTS = TEST_ID.format('explore_insights')
    CREATE_MODELS = TEST_ID.format('create_ai_models')
    DEPLOY_AND_MONITOR = TEST_ID.format('deploy_and_monitor')


class TopMenuSelectors(Enum):
    DR_LOGO = TEST_ID.format('navigation-logo')
    PROFILE_ICON = TEST_ID.format('header-open-account-menu')
    MODELS_TAB = TEST_ID.format('models')
    DEPLOYMENTS_TAB = TEST_ID.format('deployments')
    PROFILE_AND_SETTINGS_OPTION = TEST_ID.format('header-drop-profile')
    PROJECT_NAME = TEST_ID.format('project-name')


class ModelingRightSidebarSelectors(Enum):
    PAUSE_MODELING_TASKS_BUTTON = '[data-icon="pause-circle"]'
    START_MODELING_TASKS_BUTTON = '[data-icon="play-circle"]'
    WORKERS_COUNT = TEST_ID.format('current-worker-count')
    DECREASE_WORKERS_BUTTON = TEST_ID.format('decrease-workers-count')
    WORKERS_COUNT_CONTROLS = f'div.worker-settings-controls.{PENDO_HIGHLIGHT}'


class ContactSalesDialogSelectors(Enum):
    CLOSE_X_BUTTON = 'css=[data-testid="feedback-modal"] >> css=[aria-label="Close"]'
    CATEGORY_DROPDOWN = TEST_ID.format('feedback-category')
    # Enter category name, e.g. Pricing Info as a string param
    SELECTED_CATEGORY = 'span.selected-item >> ' \
                        'span.selected-item-details >> ' \
                        'span.truncate-with-tooltip >> ' \
                        'text={}'
    TEXT_AREA = TEST_ID.format('support-user-input')
    DRAG_N_DROP_ZONE = TEST_ID.format('drag-n-drop-zone')
    CHOOSE_FILE_FOR_UPLOAD_BUTTON = 'button.button.command >> label.browse-file >> text=Choose file'
    MESSAGE_SENT_TEXT = TEXT.format('Your message has been sent')
    SEND_BUTTON = TEST_ID.format('send-feedback')
    CONTACT_US_TITLE = 'header.dr-modal-header :has-text("Contact Us")'
    CATEGORY_DROPDOWN_ARROW_DOWN = f'{CATEGORY_DROPDOWN} >> i.fa.fa-chevron-down'


class DrapUsagePageSelectors(Enum):
    USAGE_CONTENT_AREA = TEST_ID.format('usage-tab')
    YOU_HAVE_N_CREDITS_TEXT = 'text=You have {} credits now. The current consumption of your credits:'


class DrapTopMenuSelectors(Enum):
    DR_LOGO = '#navigation-logo'


class PaxataLoginPageSelectors(Enum):
    CONTINUE_BUTTON = 'div.login-body :text-is("Continue")'


class DocsCommonSelectors(Enum):
    NAV_LINK = 'label.md-nav__link [href="{}"]'
    NAV_LINKS_LIST_ITEM = 'ul.md-nav__list >> li.md-nav__item [href="{}"]'
    BREADCRUMB_TITLE = 'div.breadcrumbs >> [title="{}"]'
    LAST_BREADCRUMB_TITLE = 'div.breadcrumbs >> span >> text={}'
    TOC_ITEM = 'ul.md-nav__list >> li.md-nav__item :has-text("{}")'
    TOC_NESTED_ITEM = 'ul.md-nav__list >> li.md-nav__item >> ' \
                      'ul.md-nav__list >> li.md-nav__item :has-text("{}")'
    TOC_NESTED_TWICE_ITEM = 'ul.md-nav__list >> li.md-nav__item >> ' \
                            'ul.md-nav__list >> ' \
                            'li.md-nav__item ul.md-nav__list >> ' \
                            'li.md-nav__item :has-text("{}")'


class DocsSearchSelectors(Enum):
    SEARCH_FIELD = '#search-box-input'
    TYPE_TO_START_SEARCH_TEXT = \
        'div.md-search-result__meta >> text=Type to start searching'
    N_RESULTS_FOUND = '#stats >> p >> text={} results found'
    N_RESULTS_FOUND_TEXT = '#stats :has-text("results found")'
    SEARCH_ITEM_HREF = '#search-items-list .hits-item'


class DocsMainPageSelectors(Enum):
    WELCOME_TO_DR_DOCUMENTATION_TITLE = TEXT.format(
        'Welcome to DataRobot Documentation')
    CARD_CONTAINER = 'div.card-container'
    CARD_TITLE = f'{CARD_CONTAINER} >> div.h4 >> text'
    PLATFORM_CARD_TITLE = f'{CARD_TITLE}=Platform'


class DocsPlatformPageSelectors(Enum):
    DR_PLATFORM_DOCUMENTATION_TITLE = TEXT.format(
        'DataRobot Platform Documentation')
    DATA_CARD_TITLE = f'{DocsMainPageSelectors.CARD_TITLE.value}=Data'
