from time import sleep
import logging

from pytest import mark

from utils.data_enums import (
    CreditPackType,
    NfKeys
)
from utils.helper_funcs import utc_now_to_new_iso
from utils.constants import ASSERT_ERRORS


LOGGER = logging.getLogger(__name__)


TIMEDELTA = 'seconds'
NEW_TS_DELTA = 30
WAIT_TIME = NEW_TS_DELTA * 2
WAIT_MESSAGE = 'Waiting for %d seconds so that expiration_ts < now'
EXPIRATION_JOB_MESSAGE = 'after running credit expiration job'


@mark.credits_system
@mark.trial
def test_credits_expiration(payg_drap_user_setup_teardown,
                            app_client,
                            assert_key_value,
                            get_nf_index_by_event_type,
                            dr_account_client,
                            buy_credit_pack,
                            assert_current_balance):

    # Buy Explorer credit pack
    explorer_amount, explorer_purchase_id = buy_credit_pack(
        CreditPackType.EXPLORER.value
    )

    errors = []  # Assertion errors will be added to this list

    # Assert balance == explorer_amount
    # before updating Explorer pack expiration_ts
    assert_current_balance(
        explorer_amount,
        errors,
        f'before updating {CreditPackType.EXPLORER.value} expiration')

    # Update Explorer pack expiration_ts to now + 30 seconds
    dr_account_client.admin_update_credits_expiration(
        expiration_ts=utc_now_to_new_iso(TIMEDELTA, NEW_TS_DELTA),
        purchase_id=explorer_purchase_id)

    # Wait until Explorer pack expiration_ts < now
    LOGGER.info(WAIT_MESSAGE, WAIT_TIME)
    sleep(WAIT_TIME)

    # Assert balance is still == explorer_amount
    # after updating Explorer pack expiration_ts
    assert_current_balance(
        explorer_amount,
        errors,
        f'after updating {CreditPackType.EXPLORER.value} expiration')

    # Run credits expiration job
    dr_account_client.admin_process_expired_credits()

    # Assert balance is 0 after running credits expiration job
    assert_current_balance(0,
                           errors,
                           EXPIRATION_JOB_MESSAGE)

    nf_resp = app_client.poll_for_notifications(2)
    # Assert user received Credit Balance Alert notification
    assert_key_value('Credit Balance Alert',
                     nf_resp,
                     config_key=NfKeys.TITLE.value,
                     errors_list=errors,
                     nf_index=get_nf_index_by_event_type(
                         nf_resp,
                         'credits_system.empty_balance'))

    # Buy Explorer and Accelerator credit packs
    explorer_amount, explorer_purchase_id = buy_credit_pack(
        CreditPackType.EXPLORER.value
    )
    accelerator_amount, accelerator_purchase_id = buy_credit_pack(
        CreditPackType.ACCELERATOR.value
    )

    # Assert balance = explorer_amount + accelerator_amount
    # before updating Accelerator pack expiration_ts
    assert_current_balance(
        explorer_amount + accelerator_amount,
        errors,
        f'before updating {CreditPackType.ACCELERATOR.value} expiration')

    # Update Accelerator pack expiration_ts to now + 30 seconds
    dr_account_client.admin_update_credits_expiration(
        expiration_ts=utc_now_to_new_iso(TIMEDELTA, NEW_TS_DELTA),
        purchase_id=accelerator_purchase_id)

    # Wait until Accelerator pack expiration_ts < now
    LOGGER.info(WAIT_MESSAGE, WAIT_TIME)
    sleep(WAIT_TIME)

    # Assert balance is still explorer_amount + accelerator_amount
    # after updating Accelerator pack expiration_ts
    assert_current_balance(
        explorer_amount + accelerator_amount,
        errors,
        f'after updating {CreditPackType.ACCELERATOR.value} expiration')

    # Run credits expiration job
    dr_account_client.admin_process_expired_credits()

    # Assert balance = explorer_amount as Accelerator pack is expired now
    # after running credits expiration job
    assert_current_balance(explorer_amount,
                           errors,
                           EXPIRATION_JOB_MESSAGE)

    assert not errors, ASSERT_ERRORS.format('\n'.join(errors))
