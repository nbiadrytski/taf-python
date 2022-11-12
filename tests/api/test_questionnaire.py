from pytest import (
    fixture,
    mark
)
from utils.constants import (
    ASSERT_ERRORS,
    ERROR_JSON_KEY
)
from utils.data_enums import (
    GetProfileKeys,
    UserRole,
    ProductUsagePurpose,
    LearningTrack
)


@mark.trial
@mark.questionnaire
def test_questionnaire_director_prepare_data_paxata_data_prep(
        user_setup_and_teardown,
        app_client, assert_json_keys
):
    industry = 'Telecommunications'
    payload = {
        'industry': industry,
        'user_role': UserRole.DIRECTOR.value,
        'product_usage_purpose': ProductUsagePurpose.PREPARE_DATA.value,
        'selected_learning_track': LearningTrack.PAXATA_DATA_PREP.value,
        'welcome_video_viewed': True
    }
    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.DIRECTOR.value,
                     ProductUsagePurpose.PREPARE_DATA.value,
                     LearningTrack.PAXATA_DATA_PREP.value,
                     True)


@mark.trial
@mark.questionnaire
def test_questionnaire_business_analyst_explore_insights_ml_dev(
        user_setup_and_teardown,
        app_client, assert_json_keys
):
    industry = 'Sports Analytics'
    payload = {
        'industry': industry,
        'user_role': UserRole.BUSINESS_ANALYST.value,
        'product_usage_purpose': ProductUsagePurpose.EXPLORE_INSIGHTS.value,
               'selected_learning_track': LearningTrack.ML_DEVELOPMENT.value,
               'welcome_video_viewed': False}

    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.BUSINESS_ANALYST.value,
                     ProductUsagePurpose.EXPLORE_INSIGHTS.value,
                     LearningTrack.ML_DEVELOPMENT.value,
                     False)


@mark.trial
@mark.questionnaire
def test_questionnaire_manager_ai_models_ml_ops(user_setup_and_teardown, app_client,
                                                assert_json_keys):
    industry = 'Insurance'
    payload = {'industry': industry,
               'user_role': UserRole.PRODUCT_MANAGER.value,
               'product_usage_purpose': ProductUsagePurpose.CREATE_AI_MODELS.value,
               'selected_learning_track': LearningTrack.ML_OPERATIONS.value,
               'welcome_video_viewed': True}

    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.PRODUCT_MANAGER.value,
                     ProductUsagePurpose.CREATE_AI_MODELS.value,
                     LearningTrack.ML_OPERATIONS.value,
                     True)


@mark.trial
@mark.questionnaire
def test_questionnaire_other_deploy_and_monitor_ml_ops(user_setup_and_teardown, app_client,
                                                       assert_json_keys):
    industry = 'Banking'
    payload = {'industry': industry,
               'user_role': UserRole.OTHER.value,
               'product_usage_purpose': ProductUsagePurpose.DEPLOY_AND_MONITOR.value,
               'selected_learning_track': LearningTrack.ML_OPERATIONS.value,
               'welcome_video_viewed': False}

    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.OTHER.value,
                     ProductUsagePurpose.DEPLOY_AND_MONITOR.value,
                     LearningTrack.ML_OPERATIONS.value,
                     False)


@mark.trial
@mark.questionnaire
def test_questionnaire_novice_ds_prepare_data_paxata_data_prep(user_setup_and_teardown,
                                                               app_client, assert_json_keys):
    industry = 'Health Care'
    payload = {'industry': industry,
               'user_role': UserRole.NOVICE_DS.value,
               'product_usage_purpose': ProductUsagePurpose.PREPARE_DATA.value,
               'selected_learning_track': LearningTrack.PAXATA_DATA_PREP.value,
               'welcome_video_viewed': True}

    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.NOVICE_DS.value,
                     ProductUsagePurpose.PREPARE_DATA.value,
                     LearningTrack.PAXATA_DATA_PREP.value,
                     True)


@mark.trial
@mark.questionnaire
def test_questionnaire_software_dev_ai_models_ml_dev(user_setup_and_teardown, app_client,
                                                     assert_json_keys):
    industry = 'Gaming'
    payload = {'industry': industry,
               'user_role': UserRole.SOFTWARE_DEVELOPER.value,
               'product_usage_purpose': ProductUsagePurpose.CREATE_AI_MODELS.value,
               'selected_learning_track': LearningTrack.ML_DEVELOPMENT.value,
               'welcome_video_viewed': False}

    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.SOFTWARE_DEVELOPER.value,
                     ProductUsagePurpose.CREATE_AI_MODELS.value,
                     LearningTrack.ML_DEVELOPMENT.value,
                     False)


@mark.trial
@mark.questionnaire
def test_questionnaire_manager_deploy_and_monitor_ba(user_setup_and_teardown, app_client,
                                                     assert_json_keys):
    industry = 'media'
    payload = {'industry': industry,
               'user_role': UserRole.PRODUCT_MANAGER.value,
               'product_usage_purpose': ProductUsagePurpose.DEPLOY_AND_MONITOR.value,
               'selected_learning_track': LearningTrack.BA.value,
               'welcome_video_viewed': True}

    app_client.post_account_profile(payload)

    assert_json_keys(app_client.account_profile(),
                     industry,
                     UserRole.PRODUCT_MANAGER.value,
                     ProductUsagePurpose.DEPLOY_AND_MONITOR.value,
                     LearningTrack.BA.value,
                     True)


@mark.trial
@mark.questionnaire
@mark.skip_if_env('staging')
def test_questionnaire_fields_none_except_industry(
        user_setup_and_teardown,
        app_client, resp_text,
        get_value_from_json_response,
        env_params
):
    payload = {'industry': None,
               'user_role': None,
               'product_usage_purpose': None,
               'selected_learning_track': None,
               'welcome_video_viewed': None}

    app_client.post_account_profile(payload)
    resp = app_client.account_profile()

    errors = []
    error_text = 'Key "{}" should be null'

    actual_industry = get_value_from_json_response(
        resp,
        GetProfileKeys.INDUSTRY.value
    )
    if actual_industry is not None:
        errors.append(
            ERROR_JSON_KEY.format(
                None,
                GetProfileKeys.INDUSTRY.value,
                actual_industry))

    actual_track = get_value_from_json_response(
        resp,
        GetProfileKeys.LEARNING_TRACK.value
    )
    if actual_track is not None:
        errors.append(
            error_text.format(
                GetProfileKeys.LEARNING_TRACK.value))

    actual_usage_purpose = get_value_from_json_response(
        resp,
        GetProfileKeys.USAGE_PURPOSE.value
    )
    if actual_usage_purpose is not None:
        errors.append(
            error_text.format(
                GetProfileKeys.USAGE_PURPOSE.value))

    actual_user_role = get_value_from_json_response(
        resp,
        GetProfileKeys.USER_ROLE.value
    )
    if actual_user_role is not None:
        errors.append(
            error_text.format(
                GetProfileKeys.USER_ROLE.value)
        )
    if GetProfileKeys.WELCOME_VIDEO_VIEWED.value in resp_text(resp):
        errors.append(
            f'"{GetProfileKeys.WELCOME_VIDEO_VIEWED.value}" key '
            f'should not be in response')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.trial
@mark.questionnaire
def test_questionnaire_invalid_fields_values(user_setup_and_teardown, app_client,
                                             assert_status_code, assert_json_resp):
    payload = {'industry': 'Manufacturing',
               'user_role': 'non-existing role',
               'product_usage_purpose': 'non-existing purpose',
               'selected_learning_track': 'non-existing track',
               'welcome_video_viewed': 'yes'}

    resp = app_client.post_account_profile(payload,
                                           check_status_code=False)
    errors = []
    assert_status_code(resp, expected_code=400, errors_list=errors)
    assert_json_resp(
        resp,
        expected_resp={'status': 'error',
                       'fields':
                           {'product_usage_purpose':
                                {'0': "value doesn't match any variant",
                                 '1': 'value should be None'},
                            'user_role':
                                {'0': "value doesn't match any variant",
                                 '1': 'value should be None'},
                            'welcome_video_viewed':
                                {'0': 'value should be True or False',
                                 '1': 'value should be None'},
                            'selected_learning_track':
                                {'0': "value doesn't match any variant",
                                 '1': 'value should be None'}}},
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def assert_json_keys(get_value_from_json_response):
    def assert_keys(resp, industry, role, usage_purpose, learning_track, video_viewed):
        errors = []
        actual_industry = get_value_from_json_response(resp,
                                                       GetProfileKeys.INDUSTRY.value)
        if actual_industry != industry:
            errors.append(ERROR_JSON_KEY.format(
                industry, GetProfileKeys.INDUSTRY.value, actual_industry))

        actual_user_role = get_value_from_json_response(resp,
                                                        GetProfileKeys.USER_ROLE.value)
        if actual_user_role != role:
            errors.append(
                ERROR_JSON_KEY.format(role,
                                      GetProfileKeys.USER_ROLE.value,
                                      actual_user_role))

        actual_product_usage_purpose = get_value_from_json_response(
            resp, GetProfileKeys.USAGE_PURPOSE.value)
        if actual_product_usage_purpose != usage_purpose:
            errors.append(
                ERROR_JSON_KEY.format(usage_purpose,
                                      GetProfileKeys.USAGE_PURPOSE.value,
                                      actual_product_usage_purpose))

        actual_learning_track = get_value_from_json_response(resp,
                                                             GetProfileKeys.LEARNING_TRACK.value)
        if actual_learning_track != learning_track:
            errors.append(
                ERROR_JSON_KEY.format(learning_track,
                                      GetProfileKeys.LEARNING_TRACK.value,
                                      actual_learning_track))

        actual_video_viewed = get_value_from_json_response(
            resp, GetProfileKeys.WELCOME_VIDEO_VIEWED.value)
        if actual_video_viewed != video_viewed:
            errors.append(
                ERROR_JSON_KEY.format(video_viewed,
                                      GetProfileKeys.WELCOME_VIDEO_VIEWED.value,
                                      actual_video_viewed))
        assert not errors, ASSERT_ERRORS.format('\n'.join(errors))

    return assert_keys
