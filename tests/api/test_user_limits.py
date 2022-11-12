from pytest import (
    fixture,
    mark
)

from utils.constants import (
    PAYG_STAGING_PERMISSIONS,
    PAYG_APP2_PERMISSIONS,
    ERROR_JSON_KEY
)
from utils.data_enums import (
    GetProfileKeys,
    FeatureFlags,
    Envs
)


WRONG_PERMISSIONS = 'Wrong PayAsYouGoUser permissions'


@fixture
def account_profile(app_client):
    return app_client.account_profile()


@mark.trial
@mark.limits
def test_user_permissions(
        user_setup_and_teardown, account_profile, resp_json, env_params):

    actual_permissions = resp_json(account_profile)[
        GetProfileKeys.PERMISSIONS.value]

    if FeatureFlags.ENABLE_GENERALIZED_SCORING_CODE.value not in \
            actual_permissions:
        del PAYG_STAGING_PERMISSIONS[
            FeatureFlags.ENABLE_GENERALIZED_SCORING_CODE.value
        ]
        del PAYG_APP2_PERMISSIONS[
            FeatureFlags.ENABLE_GENERALIZED_SCORING_CODE.value]

    if FeatureFlags.MANAGED_DEV_FEATURE.value not in \
            actual_permissions:
        del PAYG_STAGING_PERMISSIONS[
            FeatureFlags.MANAGED_DEV_FEATURE.value]

    if FeatureFlags.ENABLE_USER_DEFAULT_WORKERS.value not in \
            actual_permissions:
        del PAYG_STAGING_PERMISSIONS[
            FeatureFlags.ENABLE_USER_DEFAULT_WORKERS.value]

    if FeatureFlags.ALLOW_KUBEWORKERS_JOB_SUBMISSION.value not in \
            actual_permissions:
        del PAYG_STAGING_PERMISSIONS[
            FeatureFlags.ALLOW_KUBEWORKERS_JOB_SUBMISSION.value]
        del PAYG_APP2_PERMISSIONS[
            FeatureFlags.ALLOW_KUBEWORKERS_JOB_SUBMISSION.value]

    if Envs.PROD.value in env_params[0]:
        assert actual_permissions == PAYG_APP2_PERMISSIONS, \
            WRONG_PERMISSIONS
    else:
        assert actual_permissions == PAYG_STAGING_PERMISSIONS, \
            WRONG_PERMISSIONS


@mark.trial
@mark.limits
def test_max_app_count(user_setup_and_teardown,
                       account_profile,
                       resp_json):
    expected_value = 5
    actual_value = resp_json(
        account_profile)[GetProfileKeys.MAX_APP_COUNT.value]

    assert actual_value == expected_value, \
        ERROR_JSON_KEY.format(expected_value,
                              GetProfileKeys.MAX_APP_COUNT.value,
                              actual_value)


@mark.trial
@mark.limits
def test_max_eda_workers(user_setup_and_teardown,
                         account_profile,
                         resp_json):
    expected_value = 200
    actual_value = resp_json(
        account_profile)[GetProfileKeys.MAX_EDA_WORKERS.value]

    assert actual_value == expected_value, \
        ERROR_JSON_KEY.format(expected_value,
                              GetProfileKeys.MAX_EDA_WORKERS.value,
                              actual_value)


@mark.trial
@mark.limits
def test_max_ram(user_setup_and_teardown, account_profile, resp_json):

    expected_value = 30000
    actual_value = resp_json(
        account_profile
    )[GetProfileKeys.MAX_RAM_CONSTRAINTS.value][GetProfileKeys.GROUP_LIMIT.value]

    assert actual_value == expected_value, \
        ERROR_JSON_KEY.format(expected_value,
                              GetProfileKeys.GROUP_LIMIT.value,
                              actual_value)


@mark.trial
@mark.limits
def test_upload_size(user_setup_and_teardown, account_profile,
                     resp_json, env_params):

    staging_expected_value = 5368709120
    app2_expected_value = 209715200

    actual_value = resp_json(
        account_profile)[GetProfileKeys.MAX_UPLOAD_SIZE.value]

    if Envs.PROD.value in env_params[0]:
        assert actual_value == app2_expected_value, \
            ERROR_JSON_KEY.format(app2_expected_value,
                                  GetProfileKeys.MAX_UPLOAD_SIZE.value,
                                  actual_value)
    else:
        assert actual_value == staging_expected_value, \
            ERROR_JSON_KEY.format(staging_expected_value,
                                  GetProfileKeys.MAX_UPLOAD_SIZE.value,
                                  actual_value)


@mark.trial
@mark.limits
def test_workers(user_setup_and_teardown,
                 account_profile,
                 resp_json):

    expected_value = 20
    actual_value = resp_json(
        account_profile)[GetProfileKeys.MAX_WORKERS.value]

    assert actual_value == expected_value, \
        ERROR_JSON_KEY.format(expected_value,
                              GetProfileKeys.MAX_WORKERS.value,
                              actual_value)
