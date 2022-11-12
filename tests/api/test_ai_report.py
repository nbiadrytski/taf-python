from re import sub

from pytest import (
    mark,
    raises,
    fixture
)

from utils.constants import (
    ANIMALS_DATASET,
    ANIMALS_TARGET,
    AI_REPORT_CONTENT,
    AI_REPORT_TABLES_DATA,
    STATUS_CODE,
    ASSERT_ERRORS
)
from utils.helper_funcs import (
    delete_file,
    file_content
)
from utils.docx_parser import DocxParser
from utils.data_enums import (
    ModelingMode,
    Envs
)


@mark.ai_report
def test_validate_ai_report(user_setup_and_teardown,
                            finish_modeling,
                            prepare_report,
                            generate_and_download_report,
                            prepare_expected_data):

    project_id = finish_modeling
    report_file = generate_and_download_report(project_id)

    expected_text, \
    expected_tables_data = prepare_expected_data

    report_text, report_images_count, \
    report_tables_data = prepare_report(report_file)

    # delete downloaded AI report file
    delete_file(report_file)

    errors = []

    if expected_text != report_text.strip():
        errors.append(
            f'Expected report text: {expected_text}, '
            f'but got: {report_text}')

    if report_images_count != 3:
        errors.append(
            f'Expected 3 images in the report, '
            f'got {report_images_count}')

    if report_tables_data != expected_tables_data:
        errors.append(
            f'Expected tables data: {expected_tables_data},'
            f' but got: {report_tables_data}')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.ai_report
def test_generate_ai_report_until_autopilot_is_done(
        user_setup_and_teardown,
        start_modeling,
        app_client
):
    project_id = start_modeling

    # try to generate AI Report until modeling is done
    with raises(AssertionError) as error:
        app_client.generate_ai_report(project_id)

    expected_message = 'Autopilot must finish before ' \
                       'DataRobot can generate the AI report'
    errors = []

    if STATUS_CODE.format(422) not in str(error.value):
        errors.append(
            f'Expected 422 status code, got: {str(error.value)}')

    if expected_message not in str(error.value):
        errors.append(
            f'Expected "{expected_message}" in response, '
            f'got: {str(error.value)}')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def finish_modeling(setup_project,
                    app_client):
    """
    1. Creates animals.csv project
    2. Sets 'visible' target
    3. Starts modeling in quick mode
    4. Waits until modeling is finished
    Yields project_id
    """
    project_id = setup_project(
        ANIMALS_DATASET,
        ANIMALS_TARGET
    )
    app_client.v2_start_autopilot(
        project_id,
        ANIMALS_TARGET,
        ModelingMode.QUICK.value,
        blend_best_models=False
    )
    app_client.v2_poll_for_autopilot_done(
        project_id
    )
    yield project_id


@fixture
def generate_and_download_report(app_client):
    """Generates report and downloads report file"""
    def generate_and_download_report(project_id):
        report_url = app_client.generate_ai_report(
            project_id
        )
        report_file = app_client.download_ai_report(
            report_url
        )
        return report_file

    return generate_and_download_report


@fixture
def prepare_report(delete_dynamic_data):
    """
    Prepares report content before assertions:
    1. Gets report text from file
    2. Deletes dynamic data from report text
    3. Gets number of images in report
    4. Gets report tables data
    Returns report text, images count and tables data
    """
    def prepare_report(report_file):
        report_doxc = DocxParser(report_file)

        # get report text content
        report_text = ' '.join(
            report_doxc.get_docx_text()
        )
        report_text = delete_dynamic_data(report_text)

        # get number of images in the report
        report_images_count = len(
            report_doxc.get_docx_images())

        # get report tables data
        # exclude dynamic 2 last elements
        # Speed and LogLoss values from Top Models table
        report_tables_data = ' '.join(
            report_doxc.get_docx_table_data()[:-2]
        )
        report_tables_data = delete_dynamic_data(
            report_tables_data
        )
        return report_text, report_images_count, \
               report_tables_data

    return prepare_report


@fixture
def delete_dynamic_data():
    """
    Deletes dynamic data from report by regexp:
    e.g. BP49 and M35
    """
    def delete_dynamic_data(report):
        # BP49
        no_bp_content = sub(
            r'BP\d{2}', '', report
        )  # M35
        final_content = sub(
            r'M\d{2}', '', no_bp_content
        )
        return final_content

    return delete_dynamic_data


@fixture
def prepare_expected_data(env_params):

    if Envs.STAGING.value in env_params[0]:
        expected_text = file_content(AI_REPORT_CONTENT).replace(
            Envs.PROD.value, Envs.STAGING.value
        )
    else:
        expected_text = file_content(AI_REPORT_CONTENT)

    expected_tables_data = file_content(AI_REPORT_TABLES_DATA)

    yield expected_text, expected_tables_data


@fixture
def start_modeling(setup_project, app_client):
    # create animals.csv project and set 'visible' target
    project_id = setup_project(
        ANIMALS_DATASET,
        ANIMALS_TARGET
    )
    # start Autopilot in quick mode
    app_client.v2_start_autopilot(
        project_id,
        ANIMALS_TARGET,
        ModelingMode.QUICK.value
    )
    yield project_id
