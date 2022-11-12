from enum import Enum

from pytest import (
    mark,
    fixture
)

from utils.constants import ASSERT_ERRORS
from utils.selectors_enums import NewPageSelectors
from pages.docs_file_types_page import DocsFileTypesPage
from utils.data_enums import Envs


DATASET_REQUIREMENTS = 'Datasets Requirements'
STAGING_DATASET_MAX_SIZE = '5.00 GB'
PROD_DATASET_MAX_SIZE = '200 MB'


@mark.ui
def test_datasets_requirements(
        setup_and_sign_in_payg_user, new_page, home_page,
        assert_element_is_present,
        validate_dataset_requirements_modal_content
):
    setup_and_sign_in_payg_user()

    # Assertion errors will be stored in errors list
    errors = []

    home_page.continue_from_ml_dev()
    # ------------------------------------------------------------------
    # 1. Datasets Requirements description text is present at /new page
    # ------------------------------------------------------------------
    assert_element_is_present(
        new_page, NewPageSelectors.DATASETS_REQUIREMENTS.value, errors,
        f'{DATASET_REQUIREMENTS} text must be present at /new page')

    # ------------------------------------------------------------------
    # 2. Open Datasets Requirements modal and validate its content
    # ------------------------------------------------------------------
    new_page.view_dataset_requirements()
    validate_dataset_requirements_modal_content(errors)

    # ------------------------------------------------------------------
    # 3. Close Datasets Requirements modal with Close X button
    # ------------------------------------------------------------------
    new_page.close_dataset_requirements_modal()

    # ------------------------------------------------------------------
    # 4. Open and close Datasets Requirements modal with 'Got it' button
    # ------------------------------------------------------------------
    new_page.view_dataset_requirements()
    new_page.click_dataset_requirements_modal_got_it()

    # ------------------------------------------------------------------
    # 5. Open /docs/load/file-types.html page by clicking
    #    Datasets Requirements modal 'Learn more' button
    # ------------------------------------------------------------------
    # TODO: the uncomment the below 2 lines once SELF-2938 is fixed
    # new_page.view_dataset_requirements()
    # new_page.click_dataset_requirements_modal_learn_more(DocsFileTypesPage)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def validate_dataset_requirements_modal_content(
        env_params, new_page, assert_element_is_present
):
    """Validate text content of Datasets Requirements modal."""

    def dataset_requirements_modal_content(errors_list):

        for line in MODAL_CONTENT:
            if line == \
                    DatasetRequirementsModalSelectors.MAX_DATASET_SIZE.value\
                    and Envs.PROD.value in env_params[0]:
                line = DatasetRequirementsModalSelectors.\
                    MAX_DATASET_SIZE.value.replace(
                    STAGING_DATASET_MAX_SIZE, PROD_DATASET_MAX_SIZE)

                assert_element_is_present(
                    new_page, line, errors_list,
                    f'Check {DATASET_REQUIREMENTS} modal content')

    return dataset_requirements_modal_content


class DatasetRequirementsModalSelectors(Enum):
    MODAL_BODY = 'div.dr-modal-body'
    TOP_TEXT = f'{MODAL_BODY} >> p >> ' \
               f'text=Are you ready to experience the power of AI?'
    TOP_TEXT_SUBTEXT = f'{MODAL_BODY} >> p.sub-text >> text=' \
                       f'Follow these dataset requirements to put your ' \
                       f'project on the fast-track to success.'
    REQUIREMENTS_LIST = f'{MODAL_BODY} >> ul >> li >>'
    SUPPORTED_FILES = f'{REQUIREMENTS_LIST} text=Supported file types: ' \
                      f'.csv, .tsv, .dsv, .xls, .xlsx, .sas7bdat, .geojson,' \
                      f' .bz2, .gz, .zip, .tar, .tgz'
    SUPPORTED_VARS = f'{REQUIREMENTS_LIST} text=Supported variable types: ' \
                      f'numeric, categorical, boolean, text, date, currency,' \
                     f' percentage, length, and image'
    MAX_DATASET_SIZE = f'{REQUIREMENTS_LIST} ' \
                       f'text=Maximum dataset size: 5.00 GB'
    MIN_ROWS = f'{REQUIREMENTS_LIST} text=Minimum rows allowed: 20'
    PROHIBITED_DATA = f'{REQUIREMENTS_LIST} text=Datasets containing the ' \
                      f'following categories of data are prohibited:'
    PROHIBITED_DATA_LIST = f'{REQUIREMENTS_LIST} >> ul >> li >>'
    PROHIBITED_DATA_1 = 'Data regulated by the Payment Card Industry Data ' \
                        'Security Standards, or other financial account ' \
                        'numbers or credentials'
    PROHIBITED_DATA_2 = 'Information regulated by the U.S. Health Insurance ' \
                        'Portability and Accountability Act'
    PROHIBITED_DATA_3 = 'Social security numbers, driver’s license numbers ' \
                        'or other government ID numbers'
    PROHIBITED_DATA_4 = 'Sensitive personal data (as defined under the E.U. ' \
                        'General Data Protection Regulation)'
    PROHIBITED_DATA_5 = 'Personal data of individuals under 16 years olds'
    PROHIBITED_DATA_6 = 'Information subject to regulation or protection ' \
                        'under the U.S. Gramm-Leach-Bliley Act, U.S. ' \
                        'Children’s Online Privacy Protection Act or ' \
                        'similar foreign or domestic laws'
    LEARN_MORE_BUTTON = f'footer.dr-modal-footer >> div >> ' \
                        f'a.anchor.button.secondary :has-text("Learn more")'


MODAL_CONTENT = [
    DatasetRequirementsModalSelectors.TOP_TEXT.value,
    DatasetRequirementsModalSelectors.TOP_TEXT_SUBTEXT.value,
    DatasetRequirementsModalSelectors.SUPPORTED_FILES.value,
    DatasetRequirementsModalSelectors.SUPPORTED_VARS.value,
    DatasetRequirementsModalSelectors.MAX_DATASET_SIZE.value,
    DatasetRequirementsModalSelectors.MIN_ROWS.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA_1.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA_2.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA_3.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA_4.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA_5.value,
    DatasetRequirementsModalSelectors.PROHIBITED_DATA_6.value,
]
