"""Credits System conftest.py"""

import logging

from pytest import fixture

from utils.helper_funcs import (
    user_identity,
    delete_ms_from_ts,
    utc_to_iso,
    utc_now_to_new_iso
)
from utils.constants import PORTAL_ID_KEY
from utils.data_enums import (
    CreditPackType,
    CreditUsageSummaryKeys,
    Envs
)


LOGGER = logging.getLogger(__name__)


@fixture
def payg_drap_user_setup_teardown(app_client,
                                  dr_account_client):

    # Create and sign up PayAsYouGoUser
    username, first_name, last_name = user_identity()
    user_id = app_client.setup_self_service_user(
        username,
        first_name,
        last_name
    )
    # Register DRAP user
    dr_account_client.register_user(
        username,
        first_name,
        last_name
    )
    payload = {
        PORTAL_ID_KEY: dr_account_client.portal_id,
        'admin': False,
        'creditsUser': True
    }
    # Add creditsUser role to DRAP user
    dr_account_client.admin_update_role(payload)

    yield app_client, user_id

    # Delete PayAsYouGoUser
    app_client.v2_delete_payg_user(user_id)
    # Delete DRAP user
    dr_account_client.delete_user(
        dr_account_client.portal_id)


@fixture
def grant_credits(dr_account_client):
    def grant_credits_(amount):
        dr_account_client.admin_adjust_balance(amount)
    return grant_credits_


@fixture
def credit_packs(env_params):
    """
    Depending on the environment,
    returns credit pack id and credit amount
    """

    def packs(pack_type):
        credit_amount_key = 'credit_amount'
        id_key = 'id'

        explorer_prod = {
            id_key: 'prod_IUMpGwmDGSOvD5',
            credit_amount_key: 4000
        }
        accelerator_prod = {
            id_key: 'prod_IUMqdlGgbZGUf7',
            credit_amount_key: 20000
        }
        explorer_staging = {
            id_key: 'prod_IUexvR3CTuX9Vg',
            credit_amount_key: 4000
        }
        accelerator_staging = {
            id_key: 'prod_IUezulxOGLMKp8',
            credit_amount_key: 20000
        }

        if Envs.PROD.value in env_params[0]:
            if pack_type == CreditPackType.EXPLORER.value:
                return explorer_prod[id_key], \
                       explorer_prod[credit_amount_key]

            return accelerator_prod[id_key], \
                   accelerator_prod[credit_amount_key]

        if pack_type == CreditPackType.EXPLORER.value:
            return explorer_staging[id_key], \
                   explorer_staging[credit_amount_key]

        return accelerator_staging[id_key], \
               accelerator_staging[credit_amount_key]

    return packs


@fixture
def checkout_created_ts(dr_account_client, resp_json):
    """
    Returns "created" key for given "productName" (credit pack) from
    GET api/billing/getCheckoutHistory?portalId={portalId} response
    """
    def checkout_created_ts(credit_pack_name):

        checkouts = resp_json(
            dr_account_client.get_checkout_history()
        )
        checkout = [
            checkout for checkout in checkouts
            if checkout['productName'] == credit_pack_name
        ]
        if checkout:
            created_ts = checkout[0]['created']
            LOGGER.info(
                'Found created_ts %s for pack %s',
                created_ts, credit_pack_name
            )
            return created_ts

    return checkout_created_ts


@fixture
def assert_current_balance(app_client):
    """
    Asserts if current balance returned in
    GET api/v2/creditsSystem/creditBalanceSummary/ == expected_balance
    """
    def assert_balance(expected_balance,
                       errors_list,
                       message):

        actual_balance = app_client.v2_get_current_credit_balance()

        if actual_balance != expected_balance:
            errors_list.append(
                f'Expected balance {expected_balance}, '
                f'got {actual_balance} {message}')

    return assert_balance


@fixture
def buy_credit_pack(dr_account_client,
                    credit_packs,
                    checkout_created_ts):
    """
    Checks out a credit pack using POST api/billing/createCheckout.
    Then registers the checked out credit purchase using
    POST api/admin/creditsSystem/registerCreditPurchase.
    """
    def buy_pack(credit_pack_name):
        # Get pack id and amount in credits
        pack_id, amount = credit_packs(credit_pack_name)
        # Checkout a pack
        purchase_id = dr_account_client.admin_create_checkout(
            pack_id
        )
        # Get pack created_ts key from checkouts history
        created_ts = checkout_created_ts(credit_pack_name)
        # Register Explorer pack purchase
        dr_account_client.admin_register_credit_purchase(
            amount,
            purchase_id,
            delete_ms_from_ts(created_ts)
        )
        return amount, purchase_id

    return buy_pack


@fixture
def category_credit_usage(app_client,
                          get_value_from_json_response):
    """
    Returns the value [segments][0][creditUsage] key
    from GET api/v2/creditsSystem/creditUsageSummary/ response
    """
    def credit_usage(category_name):

        resp = app_client.v2_get_credit_usage_summary(
            billing_period_start_ts=utc_to_iso(),
            segment_by='category'
        )
        categories = get_value_from_json_response(
            resp,
            CreditUsageSummaryKeys.DATA.value
        )
        category = [
            category for category in categories
            if category[CreditUsageSummaryKeys.KEY.value] == category_name
        ]
        if category:
            usage = category[0]['segments'][0]['creditUsage']
            LOGGER.info(
                'creditUsage is %d for %s category',
                usage, category_name
            )
            return usage

    return credit_usage


@fixture
def get_today_start_and_end_iso_ts():
    """
    Returns current ts in iso format (start_ts),
    e.g. 2020-12-18T16:40:53+00:00
    and adds time_delta value (hours, minutes, etc.)
    to end_ts (same format as start_ts)
    """
    def start_and_end_iso_ts(time_delta='hours', value=23):
        start_ts = utc_to_iso(change_date=False, days=0)
        end_ts = utc_now_to_new_iso(time_delta, value)

        LOGGER.info('start_ts: %s, end_ts: %s', start_ts, end_ts)

        return start_ts, end_ts

    return start_and_end_iso_ts
