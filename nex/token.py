"""
Basic settings for an NEP5 Token and crowdsale
"""

from boa.interop.Neo.Storage import *

TOKEN_NAME = 'NEX Template V2'

TOKEN_SYMBOL = 'NXT2'

TOKEN_DECIMALS = 8

# This is the script hash of the address for the owner of the token
# This can be found in ``neo-python`` with the walet open, use ``wallet`` command
TOKEN_OWNER = b'S\xefB\xc8\xdf!^\xbeZ|z\xe8\x01\xcb\xc3\xac/\xacI)'

TOKEN_CIRC_KEY = b'in_circulation'

TOKEN_TOTAL_SUPPLY = 10000000 * 100000000  # 10m total supply * 10^8 ( decimals)

TOKEN_INITIAL_AMOUNT = 2500000 * 100000000  # 2.5m to owners * 10^8

# for now assume 1 dollar per token, and one neo = 40 dollars * 10^8
TOKENS_PER_NEO = 40 * 100000000

# for now assume 1 dollar per token, and one gas = 20 dollars * 10^8
TOKENS_PER_GAS = 20 * 100000000

# maximum amount you can mint in the limited round ( 500 neo/person * 40 Tokens/NEO * 10^8 )
MAX_EXCHANGE_LIMITED_ROUND = 500 * 40 * 100000000

# when to start the crowdsale
BLOCK_SALE_START = 755000

# when to end the initial limited round
LIMITED_ROUND_END = 755000 + 10000

KYC_KEY = b'kyc_ok'

LIMITED_ROUND_KEY = b'r1'


def crowdsale_available_amount(ctx):
    """

    :return: int The amount of tokens left for sale in the crowdsale
    """

    in_circ = Get(ctx, TOKEN_CIRC_KEY)

    available = TOKEN_TOTAL_SUPPLY - in_circ

    return available


def add_to_circulation(ctx, amount):
    """
    Adds an amount of token to circlulation

    :param amount: int the amount to add to circulation
    """

    current_supply = Get(ctx, TOKEN_CIRC_KEY)

    current_supply += amount
    Put(ctx, TOKEN_CIRC_KEY, current_supply)
    return True


def get_circulation(ctx):
    """
    Get the total amount of tokens in circulation

    :return:
        int: Total amount in circulation
    """
    return Get(ctx, TOKEN_CIRC_KEY)
