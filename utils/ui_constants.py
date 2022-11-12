"""Contains common variables and constants used across UI tests"""

# Timeouts
DEFAULT_TIMEOUT = 60000  # ms
ELEM_NOT_FOUND_TIMEOUT = 10000
PENDO_TOUR_CONTAINER_TIMEOUT = 5000
WAIT_FOR_MODEL_TIMEOUT = 400000

SCREENSHOTS_PATH = 'ui/screenshots'
DOWNLOADS_PATH = 'ui/downloads'

# Error messages
ELEMENT_NOT_FOUND_MESSAGE = 'Element with selector {} was not found. {}.'
ELEMENT_FOUND_MESSAGE = 'Found element with selector {}, but element should be absent. {}.'
ATTR_VALUE_NOT_CONTAINS_MESSAGE = '"{}" attribute with value "{}" of element with selector {} does not contain "{}". {}'
ATTR_VALUE_NOT_EQUALS_MESSAGE = '"{}" attribute with value "{}" of element with selector {} != "{}". {}.'
ATTR_VALUE_NOT_EQUALS_WARN_LOG_MESSAGE = 'Value "%s" of attribute "%s" != "%s"'
ATTR_VALUE_EQUALS_INFO_LOG_MESSAGE = 'Value "%s" of attribute "%s" == "%s"'
INNER_TEXT_NOT_EQUALS_MESSAGE = 'Inner text "{}" of element with selector {} != "{}". {}'
INNER_TEXT_NOT_EQUALS_LOG_MESSAGE = 'Inner text "%s" of element with selector %s != "%s"'

CARD_IS_SELECTED_VALUE = 'card-container card-content selected'

# Pendo
PENDO_HOME_TOUR_GUIDE_ID = 'R609QK8MuMz3-8ULkS449XP5QGo'

NO_TOUR_IF_CLOSED_WITH_YES_BUTTON = 'Tour must not appear again if closed with "Yes" button ' \
                                    'from "Was this tour helpful?" section'
NO_TOUR_IF_CLOSED_WITH_NO_BUTTON = 'Tour must not appear again if closed with "No" button ' \
                                   'from "Was this tour helpful?" section'
NO_TOUR_IF_CLOSED_WITH_X_BUTTON = 'Tour must not appear again if closed with X button'

PENDO_HIGHLIGHT = 'pendo-target-highlight'

COMPUTE_PREDICTIONS_BUTTON = '"Compute and download predictions" button'
