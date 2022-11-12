import logging
from urllib.parse import urlparse
from time import sleep

import requests
from pytest import (
    fixture,
    mark
)

from utils.constants import (
    TEN_K_DIABETES_DATASET,
    TEN_K_DIABETES_TARGET,
    ASSERT_ERRORS,
    DEFAULT_USER_NOTIFICATIONS,
    ERROR_JSON_RESP,
    EUCLIDIAN_DISTANCE_MODEL,
    ANIMALS_DATASET,
    ANIMALS_TARGET,
    ENABLE_AUTOPILOT_EMAIL_NOTIFICATION,
    NF_ERROR_TEXT,
    NF_IS_READ,
    NF_IS_UNREAD
)
from utils.clients import AppClient
from utils.helper_funcs import user_identity
from utils.data_enums import (
    NfKeys,
    ModelingMode
)
from utils.data_enums import FeatureFlags


LOGGER = logging.getLogger(__name__)

# notifications eventTypes
AUTOPILOT_DONE_EVENT = 'autopilot.complete'
PROJECT_SHARED_EVENT = 'project.shared'
COMMENT_CREATED_EVENT = 'comment.created'
COMMENT_UPDATED_EVENT = 'comment.updated'

NF_PERMISSIONS = {
    FeatureFlags.EXPERIMENTAL_API_ACCESS.value: True,
    FeatureFlags.ENABLE_NOTIFICATION_CENTER.value: True,
    FeatureFlags.ENABLE_USER_PUSH_NOTIFICATIONS.value: True
}
# error texts
PROJECT_JUST_SHARED = 'right after project has been shared'
AUTOPILOT_JUST_FINISHED = 'right after project has been shared'
MENTION_NO_SHARED = 'right after user has been mentioned (without project sharing)'


@fixture
def app_client(env_params):
    return AppClient(env_params, requests.Session())


@fixture
def pro_user_setup(app_client):

    username, first_name, last_name = user_identity()
    app_client.create_user(username, first_name, last_name)

    yield app_client, username, first_name, last_name


@fixture
def payg_user_setup_and_teardown(identity,
                                 app_client):

    username, first_name, last_name = identity
    invite_link = app_client.create_payg_user(
        username,
        first_name,
        last_name
    )
    app_client.open_invite_link(invite_link)
    user_id = app_client.sign_up_payg_user(
        first_name,
        last_name
    )
    app_client.v2_create_api_key()

    app_client.v2_add_feature_flag(
        FeatureFlags.ENABLE_NOTIFICATION_CENTER.value
    )
    app_client.v2_add_feature_flag(
        FeatureFlags.ENABLE_USER_PUSH_NOTIFICATIONS.value
    )
    app_client.post_account_profile(
        ENABLE_AUTOPILOT_EMAIL_NOTIFICATION
    )
    yield app_client, user_id, username

    app_client.v2_delete_payg_user(user_id)


@fixture
def user_setup(pro_user_setup):
    app_client, username, _, _ = pro_user_setup

    app_client.login(username)
    app_client.v2_create_api_key()

    username, first_name, last_name = user_identity()
    user_id = app_client.create_user(username,
                                     first_name,
                                     last_name,
                                     second_user=True,
                                     add_permissions=True,
                                     new_permissions=NF_PERMISSIONS)

    app_client.post_account_profile(ENABLE_AUTOPILOT_EMAIL_NOTIFICATION)
    yield user_id, username, first_name, last_name


@fixture
def ten_k_diabetes_setup(pro_user_setup):

    app_client, _, _, _ = pro_user_setup

    pid = app_client.v2_create_project_from_file(TEN_K_DIABETES_DATASET)
    app_client.set_target(TEN_K_DIABETES_TARGET, pid)
    app_client.v2_start_autopilot(pid,
                                  TEN_K_DIABETES_TARGET,
                                  ModelingMode.MANUAL.value)
    app_client.v2_update_worker_count(pid, 4)
    app_client.poll_for_eda_done(pid, 17)
    bp_id = app_client.v2_get_blueprint_id(EUCLIDIAN_DISTANCE_MODEL,
                                           pid)
    model_id = app_client.v2_train_model(pid, bp_id)

    yield pid, model_id


@fixture
def autopilot_complete_setup(payg_user_setup_and_teardown):

    app_client, _, _ = payg_user_setup_and_teardown

    project_id = app_client.v2_create_project_from_file(ANIMALS_DATASET)
    app_client.set_target(ANIMALS_TARGET, project_id)

    app_client.v2_start_autopilot(project_id,
                                  ANIMALS_TARGET,
                                  ModelingMode.QUICK.value,
                                  blend_best_models=False)
    app_client.v2_poll_for_autopilot_done(project_id)

    yield app_client, project_id

    app_client.v2_delete_project_by_project_id(project_id)


@fixture
def project_shared_setup(pro_user_setup, user_setup):

    app_client, _, _, _ = pro_user_setup
    _, username_1, _, _ = user_setup

    project_id = app_client.v2_create_project_from_file(TEN_K_DIABETES_DATASET)

    # Share project with username_1
    app_client.v2_share_project(project_id, username_1)

    # username logs out
    app_client.logout()

    # username_1 logs in
    app_client.login(username_1)
    app_client.v2_create_api_key()

    yield app_client, project_id, username_1

    app_client.v2_delete_project_by_project_id(project_id)
    app_client.logout()


@fixture
def comment_setup(pro_user_setup, user_setup, ten_k_diabetes_setup):

    app_client, _, _, _ = pro_user_setup
    user_id, username_1, _, _ = user_setup
    pid, model_id = ten_k_diabetes_setup

    # share project with username_1
    app_client.v2_share_project(pid, username_1)

    # leave a comment
    app_client.v2_comment(model_id, user_id)

    # username logs out
    app_client.logout()

    # username_1 logs in
    app_client.login(username_1)
    app_client.v2_create_api_key()

    yield app_client, pid, username_1

    app_client.v2_delete_project_by_project_id(pid)
    app_client.logout()


@fixture
def mention_setup(pro_user_setup, user_setup, ten_k_diabetes_setup):

    app_client, _, _, _ = pro_user_setup
    user_id, username_1, first_name, last_name = user_setup
    pid, model_id = ten_k_diabetes_setup

    # share project with username_1
    app_client.v2_share_project(pid, username_1)
    sleep(10)
    # leave a comment
    app_client.v2_comment(model_id, user_id)
    sleep(10)
    # mention username_1
    app_client.v2_comment(model_id, user_id, mention_user=True)

    # username logs out
    app_client.logout()

    # username_1 logs in
    app_client.login(username_1)
    app_client.v2_create_api_key()

    # yield app_client, pid, username_1
    yield app_client, pid, username_1, first_name, last_name

    app_client.v2_delete_project_by_project_id(pid)
    app_client.logout()


@fixture
def mention_without_share_setup(pro_user_setup, user_setup,
                                ten_k_diabetes_setup):

    app_client, _, _, _ = pro_user_setup
    user_id, username_1, first_name, last_name = user_setup
    _, model_id = ten_k_diabetes_setup

    # mention username_1
    app_client.v2_comment(model_id, user_id, mention_user=True)

    # username logs out
    app_client.logout()

    # username_1 logs in
    app_client.login(username_1)
    app_client.v2_create_api_key()

    yield app_client, username_1, first_name, last_name
    app_client.logout()


@mark.trial
@mark.notification
def test_autopilot_complete_notification(payg_user_setup_and_teardown,
                                         autopilot_complete_setup,
                                         assert_count, assert_key_is_none,
                                         assert_bool_key, assert_key_value,
                                         resp_key_by_dynamic_json_path,
                                         assert_no_nfs_left):

    _, _, username = payg_user_setup_and_teardown
    app_client, _ = autopilot_complete_setup

    # get user notifications
    resp = app_client.poll_for_notifications(expected_count=1,
                                             username=username)
    # get Project shared notification
    autopilot_id = resp_key_by_dynamic_json_path(resp, NfKeys.ID.value)

    errors = []

    # 1. Just 1 autopilot.complete notification
    assert_count(expected_count=1,
                 resp=resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=AUTOPILOT_JUST_FINISHED)
    assert_count(expected_count=1,
                 resp=resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=AUTOPILOT_JUST_FINISHED)
    # 2. next and previous keys are null
    assert_key_is_none(resp,
                       config_key=NfKeys.NEXT.value,
                       errors_list=errors,
                       error_text=AUTOPILOT_JUST_FINISHED)
    assert_key_is_none(resp,
                       config_key=NfKeys.PREVIOUS.value,
                       errors_list=errors,
                       error_text=AUTOPILOT_JUST_FINISHED)
    # 3. title is Autopilot has finished
    assert_key_value('Autopilot has finished',
                     resp,
                     config_key=NfKeys.TITLE.value,
                     errors_list=errors,
                     error_text=AUTOPILOT_JUST_FINISHED)
    # 4. eventType is autopilot.complete
    assert_key_value(AUTOPILOT_DONE_EVENT,
                     resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     error_text=AUTOPILOT_JUST_FINISHED)
    # 5. description is {first_name} {last_name} shared 10k_diabetes.csv with you
    assert_key_value('animals.csv is ready',
                     resp,
                     config_key=NfKeys.DESCRIPTION.value,
                     errors_list=errors,
                     error_text=AUTOPILOT_JUST_FINISHED)
    # 6. pushNotificationSent is False
    assert_bool_key(False,
                    resp, config_key=NfKeys.PUSH_NF_SENT.value,
                    errors_list=errors,
                    error_text=AUTOPILOT_JUST_FINISHED)
    # 7. read is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    error_text=AUTOPILOT_JUST_FINISHED)

    # read autopilot.complete notification
    app_client.v2_read_notification(autopilot_id)

    # 8. autopilot.complete notification should be read
    assert_bool_key(
        True,
        resp=app_client.v2_get_user_notifications(),
        config_key=NfKeys.READ.value,
        errors_list=errors,
        error_text='after Project shared notification has been read')

    # delete autopilot.complete notification
    app_client.v2_delete_notification(autopilot_id)

    # 9. No notifications left after autopilot.complete notification was deleted
    assert_no_nfs_left(
        resp=app_client.poll_for_notifications(expected_count=0,
                                               username=username),
        errors_list=errors,
        error_text='after Autopilot has finished notification was deleted')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
def test_project_shared_notification(pro_user_setup,
                                     project_shared_setup,
                                     assert_count,
                                     assert_key_is_none,
                                     assert_bool_key,
                                     assert_key_value,
                                     resp_key_by_dynamic_json_path,
                                     assert_no_nfs_left):

    _, _, first_name, last_name = pro_user_setup
    app_client, project_id, username_1 = project_shared_setup

    # get user notifications
    resp = app_client.poll_for_notifications(expected_count=1,
                                             username=username_1)
    # get Project shared notification
    project_shared_id = resp_key_by_dynamic_json_path(
        resp,
        NfKeys.ID.value)

    errors = []

    # 1. Just 1 Project shared notification
    assert_count(expected_count=1,
                 resp=resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=PROJECT_JUST_SHARED)
    assert_count(expected_count=1,
                 resp=resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=PROJECT_JUST_SHARED)
    # 2. next and previous keys are null
    assert_key_is_none(resp,
                       config_key=NfKeys.NEXT.value,
                       errors_list=errors,
                       error_text=PROJECT_JUST_SHARED)
    assert_key_is_none(resp,
                       config_key=NfKeys.PREVIOUS.value,
                       errors_list=errors,
                       error_text=PROJECT_JUST_SHARED)
    # 3. title is Project shared
    assert_key_value('Project shared',
                     resp,
                     config_key=NfKeys.TITLE.value,
                     errors_list=errors,
                     error_text=PROJECT_JUST_SHARED)
    # 4. eventType is project.shared
    assert_key_value(PROJECT_SHARED_EVENT,
                     resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     error_text=PROJECT_JUST_SHARED)
    # 5. description is {first_name} {last_name} shared 10k_diabetes.csv with you
    assert_key_value(
        f'{first_name} {last_name} shared 10k_diabetes.csv with you',
        resp,
        config_key=NfKeys.DESCRIPTION.value,
        errors_list=errors,
        error_text=PROJECT_JUST_SHARED)
    # 6. pushNotificationSent is False
    assert_bool_key(False,
                    resp, config_key=NfKeys.PUSH_NF_SENT.value,
                    errors_list=errors,
                    error_text=PROJECT_JUST_SHARED)
    # 7. read is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    error_text=PROJECT_JUST_SHARED)

    # read Project shared notification
    app_client.v2_read_notification(project_shared_id)

    # 8. Project shared notification should be read after filtering by read=true
    assert_bool_key(
        True,
        resp=app_client.v2_get_user_notifications(
            query_params=NF_IS_READ),
        config_key=NfKeys.READ.value,
        errors_list=errors,
        error_text='after Project shared notification has been read')

    # delete Project shared notification
    app_client.v2_delete_notification(project_shared_id)

    # 9. No notifications left after Project shared notification was deleted
    assert_no_nfs_left(
        resp=app_client.poll_for_notifications(expected_count=0,
                                               username=username_1),
        errors_list=errors,
        error_text='after Project shared notification was deleted')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
def test_mention_without_shared_notification(pro_user_setup,
                                             mention_without_share_setup,
                                             assert_count, assert_key_is_none,
                                             assert_bool_key, assert_key_value,
                                             resp_key_by_dynamic_json_path):

    _, _, first_name, last_name = pro_user_setup
    app_client, username_1, \
    user_first_name, user_last_name = mention_without_share_setup

    # get user notifications
    resp = app_client.poll_for_notifications(expected_count=1,
                                             username=username_1)
    # get New mention notification id
    mention_id = resp_key_by_dynamic_json_path(resp, NfKeys.ID.value)

    errors = []

    # 1. Just 1 New mention notification
    assert_count(expected_count=1,
                 resp=resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=MENTION_NO_SHARED)
    assert_count(expected_count=1,
                 resp=resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=MENTION_NO_SHARED)
    # 2. next and previous keys are null
    assert_key_is_none(resp,
                       NfKeys.NEXT.value,
                       errors_list=errors,
                       error_text=MENTION_NO_SHARED)
    assert_key_is_none(resp,
                       NfKeys.PREVIOUS.value,
                       errors_list=errors,
                       error_text=MENTION_NO_SHARED)
    # 3. title is New mention
    assert_key_value('New mention',
                     resp,
                     NfKeys.TITLE.value,
                     errors_list=errors,
                     error_text=MENTION_NO_SHARED)
    # 4. eventType is comment.updated
    assert_key_value(COMMENT_UPDATED_EVENT,
                     resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     error_text=MENTION_NO_SHARED)
    # 5. description is {first_name} {last_name}: {user_first_name} {user_last_name}
    assert_key_value(
        f'{first_name} {last_name}: {user_first_name} {user_last_name} ',
        resp,
        config_key=NfKeys.DESCRIPTION.value,
        errors_list=errors,
        error_text=MENTION_NO_SHARED
    )
    # 6. pushNotificationSent is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.PUSH_NF_SENT.value,
                    errors_list=errors,
                    error_text=MENTION_NO_SHARED)
    # 7. read is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    error_text=MENTION_NO_SHARED)

    # read New mention notification
    app_client.v2_read_notification(mention_id)

    # 8. New mention notification should be read (filtered by read=true)
    assert_bool_key(
        True,
        resp=app_client.v2_get_user_notifications(
            query_params=NF_IS_READ),
        config_key=NfKeys.READ.value,
        errors_list=errors,
        error_text='after New mention notification has been read')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
def test_comment_notification(pro_user_setup,
                              comment_setup,
                              assert_count,
                              resp_key_by_dynamic_json_path,
                              assert_key_is_none,
                              assert_bool_key,
                              assert_key_value,
                              assert_no_nfs_left,
                              get_nf_index_by_event_type):

    _, _, first_name, last_name = pro_user_setup
    app_client, _, username_1 = comment_setup

    # get user notifications
    resp = app_client.poll_for_notifications(
        expected_count=2,
        username=username_1
    )
    # get New comment notification index
    new_comment_index = get_nf_index_by_event_type(
        resp,
        COMMENT_CREATED_EVENT
    )
    # get New comment notification id
    new_comment_id = resp_key_by_dynamic_json_path(
        resp,
        config_key=NfKeys.ID.value,
        new_str=new_comment_index)

    errors = []
    comment_read_text = 'after New comment notification has been read'
    read_false_text = 'after filtering notifications by ?read=false'

    # 1. 2 notifications: Project shared, New comment
    assert_count(expected_count=2,
                 resp=resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=PROJECT_JUST_SHARED)
    assert_count(expected_count=2,
                 resp=resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=PROJECT_JUST_SHARED)
    # 2. next and previous keys are null
    assert_key_is_none(resp,
                       NfKeys.NEXT.value,
                       errors_list=errors,
                       error_text=PROJECT_JUST_SHARED)
    assert_key_is_none(resp,
                       NfKeys.PREVIOUS.value,
                       errors_list=errors,
                       error_text=PROJECT_JUST_SHARED)
    # 3. title is New comment
    assert_key_value('New comment',
                     resp,
                     config_key=NfKeys.TITLE.value,
                     errors_list=errors,
                     nf_index=new_comment_index,
                     error_text=PROJECT_JUST_SHARED)
    # 4. eventType is comment.created
    assert_key_value(COMMENT_CREATED_EVENT,
                     resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     nf_index=new_comment_index,
                     error_text=PROJECT_JUST_SHARED)
    # 5. description is {first_name} {last_name}: test comment
    assert_key_value(f'{first_name} {last_name}: test comment ',
                     resp,
                     config_key=NfKeys.DESCRIPTION.value,
                     errors_list=errors,
                     nf_index=new_comment_index,
                     error_text=PROJECT_JUST_SHARED)
    # 6. pushNotificationSent is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.PUSH_NF_SENT.value,
                    errors_list=errors,
                    nf_index=new_comment_index,
                    error_text=PROJECT_JUST_SHARED)
    # 7. read is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    nf_index=new_comment_index,
                    error_text=PROJECT_JUST_SHARED)

    # read New comment notification
    app_client.v2_read_notification(new_comment_id)

    # filter notifications by read=true
    read_nfs_resp = app_client.v2_get_user_notifications(
        query_params=NF_IS_READ)

    # 8. Just 1 read notification
    assert_count(expected_count=1,
                 resp=read_nfs_resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=comment_read_text)
    assert_count(expected_count=1,
                 resp=read_nfs_resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=comment_read_text)
    # 9. eventType of read notification is comment.created
    assert_key_value(COMMENT_CREATED_EVENT,
                     resp=read_nfs_resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     error_text=comment_read_text)
    # 10. New comment notification should be read
    assert_bool_key(True,
                    resp=read_nfs_resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    error_text=comment_read_text)

    # filter notifications by read=false
    unread_nfs_resp = app_client.v2_get_user_notifications(
        query_params=NF_IS_UNREAD)

    # 11. Just 1 unread notification
    assert_count(expected_count=1,
                 resp=unread_nfs_resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=read_false_text)
    assert_count(expected_count=1,
                 resp=unread_nfs_resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=read_false_text)
    # 12. eventType of unread notification is project.shared
    assert_key_value(PROJECT_SHARED_EVENT,
                     resp=unread_nfs_resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     error_text=read_false_text)
    # 13. Project shared notification should be unread
    assert_bool_key(False,
                    resp=unread_nfs_resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    error_text=read_false_text)

    # delete read New comment and unread Project shared notifications
    app_client.v2_delete_notification(new_comment_id)
    app_client.v2_delete_notification(
        resp_key_by_dynamic_json_path(
            unread_nfs_resp,
            NfKeys.ID.value)
    )

    # 14. No notifications left
    # after Project shared and New comment notifications were deleted
    assert_no_nfs_left(
        resp=app_client.poll_for_notifications(expected_count=0,
                                               username=username_1),
        errors_list=errors,
        error_text='after read New comment and unread Project shared'
                   ' notifications were deleted')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@mark.trial
@mark.notification
@mark.skip_if_env('prod')
def test_user_mention_notification(pro_user_setup,
                                   mention_setup,
                                   assert_count,
                                   assert_bool_key,
                                   assert_key_value,
                                   get_nf_index_by_event_type,
                                   get_value_from_json_response,
                                   assert_nf_index,
                                   resp_key_by_dynamic_json_path,
                                   assert_no_nfs_left,
                                   assert_not_text_in_resp,
                                   assert_key_is_none):

    _, _, first_name, last_name = pro_user_setup
    app_client, pid, username_1, \
    user_first_name, user_last_name = mention_setup

    # get user notifications
    resp = app_client.poll_for_notifications(expected_count=3,
                                             username=username_1)
    # get New comment notification index
    new_mention_index = get_nf_index_by_event_type(
        resp,
        COMMENT_UPDATED_EVENT
    )
    # get New mention notification id
    new_mention_id = resp_key_by_dynamic_json_path(
        resp,
        config_key=NfKeys.ID.value,
        new_str=new_mention_index
    )
    # get New comment notification id
    new_comment_id = resp_key_by_dynamic_json_path(
        resp,
        config_key=NfKeys.ID.value,
        new_str=get_nf_index_by_event_type(
            resp,
            COMMENT_CREATED_EVENT)
    )
    # get Project shared notification id
    project_shared_id = resp_key_by_dynamic_json_path(
        resp,
        config_key=NfKeys.ID.value,
        new_str=get_nf_index_by_event_type(
            resp,
            PROJECT_SHARED_EVENT))

    errors = []
    limit_2_text = 'after filtering notifications by ?limit=2'
    next_page_text = \
        'after filtering notifications by ?limit=2&offset=2 (next page)'
    previous_page_text = \
        'after filtering notifications by ?limit=2&offset=0 (previous page)'
    new_mention_read_text = 'after reading New mention notification'
    index_limit_2 = '(index) after filtering notifications by limit=2'
    index_next_page_text = \
        '(index) after filtering notifications by limit=2&offset=2 (next page)'
    index_previous_page_text = \
        '(index) after filtering notifications by limit=2&offset=0 (previous page)'

    # 1. 3 notifications
    assert_count(expected_count=3,
                 resp=resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=PROJECT_JUST_SHARED)
    assert_count(expected_count=3,
                 resp=resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=PROJECT_JUST_SHARED)
    # 2. next and previous keys are null
    assert_key_is_none(resp,
                       config_key=NfKeys.NEXT.value,
                       errors_list=errors,
                       error_text=PROJECT_JUST_SHARED)
    assert_key_is_none(resp,
                       config_key=NfKeys.PREVIOUS.value,
                       errors_list=errors,
                       error_text=PROJECT_JUST_SHARED)
    # 3. title is New mention
    assert_key_value('New mention',
                     resp,
                     config_key=NfKeys.TITLE.value,
                     errors_list=errors,
                     nf_index=new_mention_index,
                     error_text=PROJECT_JUST_SHARED)
    # 4. eventType is comment.updated
    assert_key_value(COMMENT_UPDATED_EVENT,
                     resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     nf_index=new_mention_index,
                     error_text=PROJECT_JUST_SHARED)
    # 5. description is {first_name} {last_name}: {user_first_name} {user_last_name}
    assert_key_value(
        f'{first_name} {last_name}: {user_first_name} {user_last_name} ',
        resp,
        config_key=NfKeys.DESCRIPTION.value,
        errors_list=errors,
        nf_index=new_mention_index,
        error_text=PROJECT_JUST_SHARED
    )
    # 6. pushNotificationSent is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.PUSH_NF_SENT.value,
                    errors_list=errors,
                    nf_index=new_mention_index,
                    error_text=PROJECT_JUST_SHARED)
    # 7. read is False
    assert_bool_key(False,
                    resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    nf_index=new_mention_index,
                    error_text=PROJECT_JUST_SHARED)

    # get user notifications with ?limit=2
    limit_2_resp = app_client.v2_get_user_notifications(
        query_params={'limit': '2'})

    # 8. count 2, totalCount 3 with ?limit=2
    assert_count(expected_count=2,
                 resp=limit_2_resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=limit_2_text)
    assert_count(expected_count=3,
                 resp=limit_2_resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=limit_2_text)
    # 9. New comment is top, New mention is next in ?limit=2 resp
    assert_nf_index(limit_2_resp,
                    event_type=COMMENT_UPDATED_EVENT,
                    expected_index='0',
                    errors_list=errors,
                    add_text=index_limit_2)
    assert_nf_index(limit_2_resp,
                    event_type=COMMENT_CREATED_EVENT,
                    expected_index='1',
                    errors_list=errors,
                    add_text=index_limit_2)
    # 10. Project shared notification is not in ?limit=2 resp
    assert_not_text_in_resp(text=PROJECT_SHARED_EVENT,
                            resp=limit_2_resp,
                            errors_list=errors,
                            add_text=index_limit_2)

    # get url from next key in ?limit=2 response
    limit_2_next_url = get_value_from_json_response(
        limit_2_resp,
        NfKeys.NEXT.value
    )
    # call url from next key from ?limit=2 response
    limit_2_next_resp = app_client.v2_api_get_request(
        urlparse(limit_2_next_url).path,
        urlparse(limit_2_next_url).query)

    # 11. count 1, totalCount 3 from ?limit=2&offset=2 response (next page)
    assert_count(expected_count=1,
                 resp=limit_2_next_resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=next_page_text)
    assert_count(expected_count=3,
                 resp=limit_2_next_resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=next_page_text)
    # 12. project.shared is in ?limit=2&offset=2 response (next page)
    assert_nf_index(resp=limit_2_next_resp,
                    event_type=PROJECT_SHARED_EVENT,
                    expected_index='0',
                    errors_list=errors,
                    add_text=index_next_page_text)
    # 13. comment.created notification is not in limit=2&offset=2 resp
    assert_not_text_in_resp(text=COMMENT_CREATED_EVENT,
                            resp=limit_2_next_resp,
                            errors_list=errors,
                            add_text=index_next_page_text)
    # 14. comment.created notification is not in limit=2&offset=2 resp
    assert_not_text_in_resp(text=COMMENT_UPDATED_EVENT,
                            resp=limit_2_next_resp,
                            errors_list=errors,
                            add_text=index_next_page_text)

    # get url from previous key from ?limit=2&offset=2 response (next page)
    limit_2_previous_url = get_value_from_json_response(
        limit_2_next_resp,
        NfKeys.PREVIOUS.value
    )
    # call url from previous key from ?limit=2&offset=2 response (next page)
    limit_2_previous_resp = app_client.v2_api_get_request(
        urlparse(limit_2_previous_url).path,
        urlparse(limit_2_previous_url).query)

    # 15. count 2, totalCount 3 from ?limit=2&offset=0 response (previous page)
    assert_count(expected_count=2,
                 resp=limit_2_previous_resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=previous_page_text)
    assert_count(expected_count=3,
                 resp=limit_2_previous_resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=previous_page_text)
    # 16. New comment is top, New mention is next in ?limit=2 resp (previous page)
    assert_nf_index(limit_2_resp,
                    event_type=COMMENT_UPDATED_EVENT,
                    expected_index='0',
                    errors_list=errors,
                    add_text=index_previous_page_text)
    assert_nf_index(limit_2_resp,
                    event_type=COMMENT_CREATED_EVENT,
                    expected_index='1',
                    errors_list=errors,
                    add_text=index_previous_page_text)
    # 17. Project shared notification is not in ?limit=2 resp (previous page)
    assert_not_text_in_resp(text=PROJECT_SHARED_EVENT,
                            resp=limit_2_resp,
                            errors_list=errors,
                            add_text=index_previous_page_text)

    # read New mention notification
    app_client.v2_read_notification(new_mention_id)
    read_nfs_resp = app_client.v2_get_user_notifications(
        query_params=NF_IS_READ)

    # 18. Just 1 read notification
    assert_count(expected_count=1,
                 resp=read_nfs_resp,
                 config_key=NfKeys.COUNT.value,
                 errors_list=errors,
                 error_text=new_mention_read_text)
    assert_count(expected_count=1,
                 resp=read_nfs_resp,
                 config_key=NfKeys.TOTAL_COUNT.value,
                 errors_list=errors,
                 error_text=new_mention_read_text)
    # 19. eventType of read notification is comment.updated
    assert_key_value(COMMENT_UPDATED_EVENT,
                     resp=read_nfs_resp,
                     config_key=NfKeys.EVENT.value,
                     errors_list=errors,
                     error_text=new_mention_read_text)
    # 20. New comment notification should be read
    assert_bool_key(True,
                    resp=read_nfs_resp,
                    config_key=NfKeys.READ.value,
                    errors_list=errors,
                    error_text=new_mention_read_text)

    # delete all notifications
    app_client.v2_delete_notification(new_mention_id)
    app_client.v2_delete_notification(new_comment_id)
    app_client.v2_delete_notification(project_shared_id)

    # 21. No notifications left
    # after Project shared, New comment, New mention notifications were deleted
    assert_no_nfs_left(
        resp=app_client.poll_for_notifications(expected_count=0,
                                               username=username_1),
        errors_list=errors,
        error_text='after New comment, Project shared, New mention'
                   ' notifications were deleted')

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def assert_nf_is_read():
    def nf_is_read(nf_read, errors_list):
        if not nf_read:
            errors_list.append(
                NF_ERROR_TEXT.format(NfKeys.READ.value, True, nf_read))
    return nf_is_read


@fixture
def assert_nf_is_not_read():
    def nf_is_not_read(nf_read, errors_list):
        if nf_read:
            errors_list.append(
                NF_ERROR_TEXT.format(NfKeys.READ.value, False, nf_read))
    return nf_is_not_read


@fixture
def assert_nf_index(get_nf_index_by_event_type):
    def nf_index(resp, event_type, expected_index, errors_list, add_text=''):
        actual_index = get_nf_index_by_event_type(resp, event_type)
        if actual_index != expected_index:
            errors_list.append(
                NF_ERROR_TEXT.format(
                    event_type, add_text, expected_index, actual_index))
    return nf_index


@fixture
def assert_key_is_none(get_value_from_json_response):
    def is_none(resp, config_key, errors_list, error_text=''):
        actual_key = get_value_from_json_response(resp, config_key)
        if actual_key is not None:
            errors_list.append(
                NF_ERROR_TEXT.format(
                    config_key, error_text, None, actual_key))
    return is_none


@fixture
def assert_count(get_value_from_json_response):
    def count(expected_count, resp, config_key, errors_list, error_text=''):
        actual_count = get_value_from_json_response(resp, config_key)
        if actual_count != expected_count:
            errors_list.append(
                NF_ERROR_TEXT.format(
                    config_key, error_text, expected_count, actual_count))
    return count


@fixture
def assert_no_nfs_left(resp_json):
    def no_nfs_left(resp, errors_list, error_text=''):
        actual_resp = resp_json(resp)
        if actual_resp != DEFAULT_USER_NOTIFICATIONS:
            errors_list.append(
                ERROR_JSON_RESP.format(DEFAULT_USER_NOTIFICATIONS, error_text, actual_resp))
    return no_nfs_left
