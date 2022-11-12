from pytest import (
    mark,
    raises
)

from utils.constants import (
    TEN_K_DIABETES_DATASET,
    ASSERT_ERRORS,
    LIMITED_ACCESS_ERROR_CODE,
    LIMITED_ACCESS_MESSAGE,
    LIMITED_ACCESS_RESP_CODE
)


@mark.credits_system
@mark.trial
def test_create_project_after_balance_top_up(payg_drap_user_setup_teardown,
                                             app_client, grant_credits,
                                             teardown_project):
    # Make user's balance 0
    grant_credits(-1)

    # Assert user cannot create a project
    with raises(AssertionError) as error:
        app_client.v2_create_project_from_file(TEN_K_DIABETES_DATASET)

    # Make user's balance positive
    grant_credits(100)

    project_id = app_client.v2_create_project_from_file(TEN_K_DIABETES_DATASET)

    errors = []
    if not all(string in str(error.value) for string in (
                LIMITED_ACCESS_RESP_CODE, LIMITED_ACCESS_ERROR_CODE, LIMITED_ACCESS_MESSAGE)):
        errors.append(
            f'User must be able to create a project after balance top up. {error.value}')

    if len(project_id) != 24:
        errors.append(
            f'Project was not created after balance top up. ProjectId: {project_id}')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
