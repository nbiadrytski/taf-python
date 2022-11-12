import os
import re
import json
import logging
from random import randint
from time import time
from datetime import (
    datetime,
    timedelta
)
from uuid import uuid1
from operator import itemgetter
from urllib.parse import (
    urlparse,
    parse_qs
)

from pdfminer.high_level import extract_text
import dictdiffer
from jsonpath_rw import parse as json_parser

from utils.errors import UnsupportedEnvException
from utils import rfc3339
from utils.constants import (
    USER_PASSWORD,
    TEST_USER_EMAIL,
    STAGING_SELF_SERVICE_TEST_USER
)
from utils.data_enums import Envs


LOGGER = logging.getLogger(__name__)
# disable logging for 3rd party pdfminer module
logging.getLogger('pdfminer').setLevel(logging.ERROR)


def generate_user_identity(n, email_template, f_name, surname):
    """
    Builds username, first_name, last_name based on a random number with N digits.

    Parameters
    ----------
    n : int
        Desired number of digits
    email_template : str
        user email template with one variable for random uuid
    f_name : str
        User's first name
    surname : str
        User's last name

    Returns
    -------
    username, first_name, last_name : tuple
        A tuple of user's username, first_name, last_name
    """
    n_digit_number = _generate_random_number_with_n_digits(n)
    username = email_template.format(str(n_digit_number))
    first_name = f_name + str(n_digit_number)
    last_name = surname + str(n_digit_number)

    return username, first_name, last_name


def get_host(env):
    """
    Returns supported environment host.
    Raises UnsupportedEnvException if host is not in Env enum.

    Parameters
    ----------
    env : str
        E.g. 'prod', 'staging'

    Returns
    -------
    host : str
        Host string, e.g. 'https://app2.datarobot.com'
    """
    env = env.upper()
    if env not in Envs.__members__:
        raise UnsupportedEnvException(env, Envs.__members__.keys())

    return Envs.__members__.get(env).value


def get_value_by_json_path(actual_json, json_path, idx=0):
    """
    Gets json key value by json path.
    Default idx=0 to get 1st item from resulting list.

    Parameters
    ----------
    actual_json : dict
        Actual json response
    json_path : str
        Path to key
    idx : int
        First item from resulting list

    Returns
    -------
    value : str
        Key value
    """
    try:
        return [match.value for match in json_parser(
            json_path
        ).find(actual_json)][idx]
    except IndexError as error:
        LOGGER.error(
            'Did not find key value by json_path "%s" in response: %s',
            json_path, actual_json, exc_info=True
        )
        raise ValueError(
            f'Did not find key value by json_path "{json_path}"'
            f' in response: "{actual_json}". Error {error}')


def file_content(file_path):
    """
    Return file content based on provided file path.

    Parameters
    ----------
    file_path : str
        Relative path to file

    Returns
    -------
    file content : str
        File content
    """
    file_ = os.path.join(os.getcwd(), file_path)
    if os.path.isfile(file_):
        with open(file_) as f:
            return f.read()
    else:
        LOGGER.error('File %s was not found', file_)
        raise FileNotFoundError


def convert_json_to_dict(file_path):
    """
    Deserializes file-like object containing a JSON document to a dict

    Parameters
    ----------
    file_path : str
        Relative path to .json file

    Returns
    -------
    dictionary : dict
        Python dictionary
    """
    file_ = os.path.join(os.getcwd(), file_path)
    if os.path.isfile(file_):
        with open(file_) as f:
            return json.load(f)
    else:
        LOGGER.error('File %s was not found', file_)
        raise FileNotFoundError


def compare_dicts(actual_dict, expected_dict, ignored_keys):
    """
    Compare 2 dicts are equal using dictdiffer module, logs diff.
    Pass the keys to be ignored to ignore_keys param.

    Parameters
    ----------
    actual_dict : dict
        Actual dict
    expected_dict : dict
        Expected dict
    ignored_keys : tuple
        Keys to be ignored

    Returns
    -------
    bool : bool
        If two dicts are equal
    """
    difference = list(dictdiffer.diff(first=actual_dict,
                                      second=expected_dict,
                                      ignore=ignored_keys))
    if difference:
        LOGGER.error('Responses do not match:\n %s', difference)
        return False

    return True


def _generate_random_number_with_n_digits(n):
    """
    Generates random number with N digits.

    Parameters
    ----------
    n : int
        Desired number of digits

    Returns
    -------
    number : int
        Random number
    """
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1

    return randint(range_start, range_end)


def auth_header(api_key):
    """
    Returns formatted Authorization request header string.

    Parameters
    ----------
    api_key : str
        Admin's or user's API key

    Returns
    -------
    header : dict
        Authorization header
    """
    return {'Authorization': 'Bearer {}'.format(api_key)}


def update_rfc3339_date(days, ahead):
    """
    Returns string representation of rfc3339 date.
    Date can be updated ahead or back.

    Parameters
    ----------
    days : int
        N of days
    ahead : bool
        Set date ahead or back by N of days

    Returns
    -------
    date : str
        String representation of rfc3339 date
    """
    if ahead:
        return rfc3339.datetimetostr(datetime.utcnow() + timedelta(days=days))

    return rfc3339.datetimetostr(datetime.utcnow() - timedelta(days=days))


def sign_up_payload(first_name, last_name):
    """
    Returns user sign up request body.

    Parameters
    ----------
    first_name : str
        User's first name
    last_name : str
        User's last name

    Returns
    -------
    request body : dict
        Sign up user request body
    """
    payload = {
        'password': USER_PASSWORD,
        'firstName': first_name,
        'lastName': last_name,
        'passwordConfirmation': USER_PASSWORD
    }
    return payload


def user_identity():
    """
    Generates random username, first_name and last_name.

    Returns
    -------
    username, first_name, last_name : tuple
        A tuple of user's username, first_name, last_name
    """
    username, first_name, last_name = \
        generate_user_identity(n=20,
                               email_template=TEST_USER_EMAIL,
                               f_name='FirstName',
                               surname='LastName')

    LOGGER.info('User identity generated: %s, %s, %s',
                username, first_name, last_name)

    return username, first_name, last_name


def get_query_param_value(url, param):
    """
    Returns url's query parameter value by passed param name.

    Parameters
    ----------
    url : str
        Url
    param : str
        Url's query parameter name

    Returns
    -------
    param value : str
        Url's query parameter value
    """
    return parse_qs(urlparse(url).query)[param][0]


def build_blueprint_dict(model_type,
                         bp_id,
                         bp_num,
                         dataset_id,
                         samplepct=64,
                         samplerows=6400,
                         samplesize=6400):
    return {'max_reps': 1,
            'task_type': 'datarobot',
            'samplepct': samplepct,
            'samplerows': samplerows,
            'samplesize': samplesize,
            'dataset_id': dataset_id,
            'model_type': model_type,
            'blueprint_id': bp_id,
            'features': ['One-Hot Encoding',
                         'Missing Values Imputed',
                         'Standardize',
                         model_type],
            'icons': [1],
            'bp': bp_num}


def time_left(timeout_period):
    return str(timedelta(seconds=timeout_period - time())).split('.')[0]


def get_substring_by_pattern(string, pattern):
    """
    Returns a substring by the passed regexp pattern.
    E.g. if initial string is
    'attachment;filename="DataRobot%20AI%20Report%20-%202020.06.24%20-%202.54pm.docx"'
    and pattern is '"(.*?)"', then
    'DataRobot%20AI%20Report%20-%202020.06.24%20-%202.54pm.docx' will be returned

    Parameters
    ----------
    string : str
        Initial string
    pattern : str
        Regexp pattern

    Returns
    -------
    substring : str
        Substring
    """
    return re.search(pattern, string).group(1)


def delete_file(file):
    """
    Deletes a file.
    Excepts OSError if the file was not deleted.

    Parameters
    ----------
    file : str
        Relative path to file

    Returns
    -------
    substring : str
        Substring
    """
    try:
        os.remove(file)
        LOGGER.info('%s file has been deleted', file)
    except OSError as e:
        LOGGER.error('Error: %s - %s.', e.filename, e.strerror)


def insert_into_str(source_str, index, new_str):
    """
    Inserts a string into another string at given index.

    Parameters
    ----------
    source_str : str
        Source string
    index : int
        Index at which a new string should be inserted into the source string
    new_str : str
        String to insert

    Returns
    -------
    final string : str
        Source str with inserted new_str at given index
    """
    return source_str[:index] + new_str + source_str[index:]


def generate_unique_email(text=''):
    """
    Returns a unique email address,
    e.g. textb8a8b870-d7e3-11ea-af34-8c8590a52a72@test.com

    Parameters
    ----------
    text : str
        Additional text

    Returns
    -------
    email : str
        Unique email address
    """
    return f'{text}{uuid1()}@example.com'


def generate_uuid():
    """
    Returns a unique 36-character uuid,
    e.g. a027e512-fefa-11ea-816b-8c8590a52a72

    Returns
    -------
    uuid : str
        Unique 36-character uuid
    """
    return str(uuid1())


def is_iso_date_valid(date_str):
    """
    Returns True if date corresponds to iso format.

    Parameters
    ----------
    date_str : str
        Date string

    Returns
    -------
    is date valid : bool
        If date corresponds to iso format or not
    """
    try:
        # Python does not recognize 'Z'-suffix as valid
        if 'Z' in date_str:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        LOGGER.error('%s is not a valid iso date', date_str)
        return False


def portal_user_info(email):
    return {'first_name': 'PortalUserFirstName',
            'last_name': 'PortalUserLastName',
            'username': email}


def future_date(days=1, long_month=True,
                subtract_hour=True, hour_value=5):
    """
    Returns future date (timedelta=days) in format April 4, 2021 if long_month,
    otherwise Apr 4, 2021.
    Optionally subtracts hours from utcnow() date.
    ^^ This is useful in test_buy_credit_pack test where test user has Birmingham, AL Stripe shipping address,
    which is utcnow() - 5 hours.
    """
    tomorrow = datetime.utcnow() + timedelta(days=days)
    if subtract_hour:
        tomorrow = tomorrow - timedelta(hours=hour_value)
    if long_month:
        month = tomorrow.strftime('%B')
    else:
        month = tomorrow.strftime('%b')

    return f"{month} " \
           f"{tomorrow.strftime('%-d')}, " \
           f"{tomorrow.strftime('%Y')}"


def utc_to_iso(change_date=True, days=-7):
    """
    If change_date=True, adds or subtracts days to current utc date.
    Converts utc date to iso format and adds +00:00 to the end,
    e.g. 2020-12-18T16:40:53+00:00
    """
    if change_date:
        utc_in_iso = (datetime.utcnow() + timedelta(days=days)).isoformat()
        return f'{utc_in_iso.split(".")[0]}+00:00'
    return f'{datetime.utcnow().isoformat().split(".")[0]}+00:00'


def utc_now_to_new_iso(time_delta, value):
    """
    Adds or subtracts weeks/days/hours/minutes/seconds to current utc date.
    Converts utc date to iso format and adds +00:00 to the end,
    e.g. 2020-12-18T16:40:53+00:00
    """
    if time_delta == 'weeks':
        utc_in_iso = (datetime.utcnow() + timedelta(weeks=value)).isoformat()
        return f'{utc_in_iso.split(".")[0]}+00:00'
    elif time_delta == 'days':
        utc_in_iso = (datetime.utcnow() + timedelta(days=value)).isoformat()
        return f'{utc_in_iso.split(".")[0]}+00:00'
    elif time_delta == 'hours':
        utc_in_iso = (datetime.utcnow() + timedelta(hours=value)).isoformat()
        return f'{utc_in_iso.split(".")[0]}+00:00'
    elif time_delta == 'minutes':
        utc_in_iso = (datetime.utcnow() + timedelta(minutes=value)).isoformat()
        return f'{utc_in_iso.split(".")[0]}+00:00'
    elif time_delta == 'seconds':
        utc_in_iso = (datetime.utcnow() + timedelta(seconds=value)).isoformat()
        return f'{utc_in_iso.split(".")[0]}+00:00'


def delete_ms_from_ts(ts):
    """
    Deletes milliseconds from ISO timestamp string.
    E.g. before: '2021-02-09T08:39:09.720615+00:00',
    after: '2021-02-09T08:39:09+00:00'
    """
    return re.sub(r'\.(.*?)\+', '+', ts)


def text_matches_regexp(text, regexp_pattern):
    """If the text matches regular expression or not"""
    if re.match(regexp_pattern, text) is not None:
        return True
    return False


def get_id_from_url(url, index):
    """
    Extracts id string from url, e.g. if url is
    https://staging.datarobot.com/projects/60757cae0c1c5a4ddcea81ba/eda
    then a list will be returned:
    ['/staging.datarobot.com', '60757cae0c1c5a4ddcea81ba'].
    Get element at index you need.
    """
    return re.findall('/(.+?)/', url)[index]


def sort_list_of_dicts(list_of_dicts, key='category'):
    """
    Sorts list of dicts by dict key

    Parameters
    ----------
    list_of_dicts : list
        List of dicts
    key : str
        Dict key to be sorted by

    Returns
    -------
    sorted list of dicts : list
        Returns a sorted list of dicts by passed key
    """
    return sorted(list_of_dicts, key=itemgetter(key))


def sort_credits_system_data_dicts(json_resp, key='category'):
    """
    Sorts dicts from 'data' list returned by
    GET api/creditsSystem/creditUsageDetails
    """
    resp_data = {'data': sort_list_of_dicts(json_resp['data'], key)}
    resp_total_count = {'totalCount': json_resp['totalCount']}

    return {**resp_data, **resp_total_count}


def replace_chars_if_needed(string, replace_me='+', replace_with='%2B'):
    """
    If the passed char (replace_me) is present in a string,
    then it is replaced with a new char (replace_with)
    """
    if replace_me in string:
        return string.replace(replace_me, replace_with)

    return string


def get_today_start_and_end_iso_ts(time_delta='hours', value=23):
    """
    Returns current ts in iso format (start_ts),
    e.g. 2020-12-18T16:40:53+00:00
    and adds time_delta value (hours, minutes, etc.)
    to end_ts (same format as start_ts)
    """
    start_ts = utc_to_iso(change_date=False, days=0)
    end_ts = utc_now_to_new_iso(time_delta, value)

    LOGGER.info('start_ts: %s, end_ts: %s', start_ts, end_ts)

    return start_ts, end_ts


def screenshot_name(selector):
    """
    Returns UI test screenshot name in format:
    {selector_name_without_spaces}-{timestamp}.png
    """
    timestamp = datetime.now().strftime(
        '%H_%M_%S'
    )
    if ' ' in selector:  # remove spaces
        selector = selector.replace(' ', '')

    return f'{selector}-{timestamp}.png'


def extract_text_from_pdf(file_path):
    """Returns string content of .pdf file using pdfminer.six library"""

    return extract_text(file_path)


def get_digits_from_string(string):
    """Returns a list of digits found in a string"""

    return [int(char) for char in string.split() if char.isdigit()]


def register_tests():
    return {'test_non_admin_cannot_register': portal_user_info(
        TEST_USER_EMAIL.format('48417171711264854130'))}


def account_tests():
    return {
        'test_account_info': portal_user_info(
            TEST_USER_EMAIL.format('18125467771642992847')),
        'test_account_no_portal_id': portal_user_info(
            TEST_USER_EMAIL.format('53950052219539627005')),
        'test_account_portal_id_not_yours': portal_user_info(
            TEST_USER_EMAIL.format('51287084064279103867')),
        'test_account_portal_id_is_str': portal_user_info(
            STAGING_SELF_SERVICE_TEST_USER),
        'test_account_valid_non_existing_portal_id': portal_user_info(
            STAGING_SELF_SERVICE_TEST_USER),
        'test_admin_cannot_get_deleted_account': portal_user_info(
            TEST_USER_EMAIL.format('25185762945359401453')),
        'test_try_to_update_account_email': portal_user_info(
            TEST_USER_EMAIL.format('68075116541275320727')),
        'test_try_to_update_account_with_unknown_field': portal_user_info(
            TEST_USER_EMAIL.format('84275523161659572720')),
        'test_update_account_without_portal_id': portal_user_info(
            TEST_USER_EMAIL.format('86378705219868472819')),
        'test_update_not_your_account': portal_user_info(
            TEST_USER_EMAIL.format('42208676467187221155')),
        'test_update_account_after_user_is_deleted': portal_user_info(
            TEST_USER_EMAIL.format('45425186891907457064')),
        'test_update_account_only_portal_id_in_payload': portal_user_info(
            TEST_USER_EMAIL.format('17174952598691350027')),
        'test_admin_can_update_every_account': portal_user_info(
            TEST_USER_EMAIL.format('57162279772541625774'))}


def profile_tests():
    return {
        'test_profile_info': portal_user_info(
            TEST_USER_EMAIL.format('81982714175796414943')),
        'test_profile_no_portal_id': portal_user_info(
            TEST_USER_EMAIL.format('61506088027232877640')),
        'test_profile_portal_id_not_yours': portal_user_info(
            TEST_USER_EMAIL.format('87481675200753990552')),
        'test_admin_cannot_get_deleted_profile': portal_user_info(
            TEST_USER_EMAIL.format('11270123125282522303')),
        'test_profile_valid_non_existing_portal_id': portal_user_info(
            STAGING_SELF_SERVICE_TEST_USER),
        'test_update_all_profile_fields': portal_user_info(
            TEST_USER_EMAIL.format('79798019749097574878')),
        'test_update_one_profile_field': portal_user_info(
            TEST_USER_EMAIL.format('61218121017892277539')),
        'test_update_profile_without_portal_id': portal_user_info(
            TEST_USER_EMAIL.format('99814683020750343539')),
        'test_update_not_your_profile': portal_user_info(
            TEST_USER_EMAIL.format('53012784135819849118')),
        'test_update_profile_unknown_field_in_payload': portal_user_info(
            TEST_USER_EMAIL.format('23697046480675618778')),
        'test_update_profile_after_user_is_deleted': portal_user_info(
            TEST_USER_EMAIL.format('87056396497321105136')),
        'test_update_profile_only_portal_id_in_payload': portal_user_info(
            TEST_USER_EMAIL.format('23158361036524576859')),
        'test_update_profile_fields_over_max_values': portal_user_info(
            TEST_USER_EMAIL.format('71911788185979785288')),
        'test_admin_can_update_every_profile': portal_user_info(
            TEST_USER_EMAIL.format('55882866630526895375'))}


def roles_tests():
    return {
        'test_admin_get_role': portal_user_info(
            TEST_USER_EMAIL.format('12827800852805697116')),
        'test_user_cannot_get_role': portal_user_info(
            TEST_USER_EMAIL.format('80968894330864574232')),
        'test_admin_get_role_portal_id_is_str': portal_user_info(
            TEST_USER_EMAIL.format('63186753074354314090')),
        'test_admin_update_role': portal_user_info(
            TEST_USER_EMAIL.format('66600593803238796544')),
        'test_admin_update_role_with_unknown_field': portal_user_info(
            TEST_USER_EMAIL.format('85188644322033681608')),
        'test_admin_update_to_invalid_role': portal_user_info(
            TEST_USER_EMAIL.format('61639608759391191954')),
        'test_admin_update_deleted_user_role': portal_user_info(
            TEST_USER_EMAIL.format('68131395301874369264')),
        'test_admin_update_role_only_portal_id_in_payload': portal_user_info(
            TEST_USER_EMAIL.format('22417177522576594482'))
    }


def register_metering_data_tests():
    return {
        'test_register_metering_data_2nd_user_doesnt_exist': portal_user_info(
            TEST_USER_EMAIL.format('52641520386371807495')),
        'test_non_admin_cannot_register_metering_data': portal_user_info(
            TEST_USER_EMAIL.format('22888512701093100695'))
    }


def credit_usage_details_tests():
    return {
        'test_credit_usage_details_invalid_params': portal_user_info(
            TEST_USER_EMAIL.format('36916205783492820791')),
        'test_credit_usage_details_required_params_email': portal_user_info(
            TEST_USER_EMAIL.format('74701172391701160280')),
        'test_credit_usage_details_email_not_yours': portal_user_info(
            TEST_USER_EMAIL.format('55285123020247222700')),
        'test_credit_usage_details_portal_id_not_yours': portal_user_info(
            TEST_USER_EMAIL.format('78752577825329386039')),
        'test_get_credit_usage_details_for_deleted_user': portal_user_info(
            TEST_USER_EMAIL.format('75356910586692965817'))
    }


def adjust_balance_tests():
    return {
        'test_try_to_adjust_balance_below_0': portal_user_info(
            TEST_USER_EMAIL.format('25185762945359401451')),
        'test_adjust_balance_int_value_is_str': portal_user_info(
            TEST_USER_EMAIL.format('44707746839856179805')),
        'test_adjust_balance_long_reason': portal_user_info(
            TEST_USER_EMAIL.format('83668936535868753001')),
        'test_adjust_balance_both_email_and_portal_id': portal_user_info(
            TEST_USER_EMAIL.format('94530607898906541664')),
        'test_non_admin_cannot_adjust_balance': portal_user_info(
            TEST_USER_EMAIL.format('65561378274360445751')),
        'test_cannot_adjust_balance_for_deleted_user': portal_user_info(
            TEST_USER_EMAIL.format('26735592714985437407')),
    }


def adjust_balance_summary_tests():
    return {
        'test_balance_summary_invalid_query_param': portal_user_info(
            TEST_USER_EMAIL.format('39215908058431103028')),
        'test_balance_summary_both_portal_id_and_email': portal_user_info(
            TEST_USER_EMAIL.format('77295155230971289720')),
        'test_cannot_get_not_yours_balance_summary_by_email': portal_user_info(
            TEST_USER_EMAIL.format('78070303187654481840'))
    }
