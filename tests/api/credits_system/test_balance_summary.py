from pytest import (
    mark,
    fixture
)

from utils.constants import (
    ASSERT_ERRORS,
    DATASET_42_MB,
    CREDIT_BALANCE_AFTER_LAST_TRANSACTION
)
from utils.data_enums import BalanceSummaryKeys


@mark.credits_system
@mark.trial
def test_balance_summary_is_updated(payg_drap_user_setup_teardown,
                                    app_client, grant_credits,
                                    upload_1_or_2_credit_dataset,
                                    assert_key_in_resp):
    initial_credits_amount = 10
    grant_credits(initial_credits_amount)

    upload_1_or_2_credit_dataset()

    # Make sure 8 <= initial_current_balance <= 9
    initial_current_balance = app_client.poll_for_balance_range(
        min_balance=8, max_balance=9)

    errors = []
    assert_key_in_resp(
        resp=app_client.v2_get_credit_balance_summary(),
        key=BalanceSummaryKeys.BALANCE_AFTER_LAST_TRANSACTION.value,
        # balanceAfterLastCreditTransaction == 200
        # balance at last refill is no longer directly used,
        # and is fixed at 20,000 for UI purposes only
        expected_value=CREDIT_BALANCE_AFTER_LAST_TRANSACTION,
        errors_list=errors)

    credits_usage = initial_credits_amount - initial_current_balance
    # Make sure 1 <= credits_usage <= 2
    if credits_usage != 1 and credits_usage != 2:
        errors.append(
            'initial_credits_amount - initial_current_balance != 2 or 1')

    grant_credits(20)
    # Make sure 28 <= current_balance <= 29
    app_client.poll_for_balance_range(28, 29)

    assert_key_in_resp(
        resp=app_client.v2_get_credit_balance_summary(),
        key=BalanceSummaryKeys.BALANCE_AFTER_LAST_TRANSACTION.value,
        expected_value=CREDIT_BALANCE_AFTER_LAST_TRANSACTION,  # 200
        errors_list=errors)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))


@fixture
def upload_1_or_2_credit_dataset(app_client):

    def upload_dataset():
        # Upload a 1 or 2 credit dataset twice
        app_client.v2_upload_dataset_via_url(DATASET_42_MB)
        app_client.v2_upload_dataset_via_url(DATASET_42_MB)

    return upload_dataset
