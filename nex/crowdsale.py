from boa.interop.Neo.Blockchain import GetHeight
from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Storage import Get, Put
from boa.builtins import concat
from nex.token import *
from nex.txio import get_asset_attachments

# OnInvalidKYCAddress = RegisterAction('invalid_registration', 'address')
OnKYCRegister = RegisterAction('kyc_registration', 'address')
OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnRefund = RegisterAction('refund', 'addr_to', 'amount')


def kyc_register(ctx, args):
    """

    :param args:list a list of addresses to register
    :param token:Token A token object with your ICO settings
    :return:
        int: The number of addresses to register for KYC
    """
    ok_count = 0

    if CheckWitness(TOKEN_OWNER):

        for address in args:

            if len(address) == 20:

                kyc_storage_key = concat(KYC_KEY, address)
                Put(ctx, kyc_storage_key, True)

                OnKYCRegister(address)
                ok_count += 1

    return ok_count


def kyc_status(ctx, args):
    """
    Gets the KYC Status of an address

    :param args:list a list of arguments
    :return:
        bool: Returns the kyc status of an address
    """

    if len(args) > 0:
        addr = args[0]

        kyc_storage_key = concat(KYC_KEY, addr)

        return Get(ctx, kyc_storage_key)

    return False


def perform_exchange(ctx):
    """

     :param token:Token The token object with NEP5/sale settings
     :return:
         bool: Whether the exchange was successful
     """

    attachments = get_asset_attachments()  # [receiver, sender, neo, gas]

    # this looks up whether the exchange can proceed
    exchange_ok = can_exchange(ctx, attachments, False)

    if not exchange_ok:
        # This should only happen in the case that there are a lot of TX on the final
        # block before the total amount is reached.  An amount of TX will get through
        # the verification phase because the total amount cannot be updated during that phase
        # because of this, there should be a process in place to manually refund tokens
        if attachments[2] > 0:
            OnRefund(attachments[1], attachments[2])
        # if you want to exchange gas instead of neo, use this
        # if attachments.gas_attached > 0:
        #    OnRefund(attachments.sender_addr, attachments.gas_attached)
        return False

    # lookup the current balance of the address
    current_balance = Get(ctx, attachments[1])

    # calculate the amount of tokens the attached neo will earn
    exchanged_tokens = attachments[2] * TOKENS_PER_NEO / 100000000

    # if you want to exchange gas instead of neo, use this
    # exchanged_tokens += attachments[3] * TOKENS_PER_GAS / 100000000

    # add it to the the exchanged tokens and persist in storage
    new_total = exchanged_tokens + current_balance
    Put(ctx, attachments[1], new_total)

    # update the in circulation amount
    result = add_to_circulation(ctx, exchanged_tokens)

    # dispatch transfer event
    OnTransfer(attachments[0], attachments[1], exchanged_tokens)

    return True


def can_exchange(ctx, attachments, verify_only):
    """
    Determines if the contract invocation meets all requirements for the ICO exchange
    of neo or gas into NEP5 Tokens.
    Note: This method can be called via both the Verification portion of an SC or the Application portion

    When called in the Verification portion of an SC, it can be used to reject TX that do not qualify
    for exchange, thereby reducing the need for manual NEO or GAS refunds considerably

    :param attachments:Attachments An attachments object with information about attached NEO/Gas assets
    :return:
        bool: Whether an invocation meets requirements for exchange
    """

    # if you are accepting gas, use this
#        if attachments[3] == 0:
#            print("no gas attached")
#            return False

    # if youre accepting neo, use this

    if attachments[2] == 0:
        return False

    # the following looks up whether an address has been
    # registered with the contract for KYC regulations
    # this is not required for operation of the contract

#        status = get_kyc_status(attachments.sender_addr, storage)
    if not get_kyc_status(ctx, attachments[1]):
        return False

    # caluclate the amount requested
    amount_requested = attachments[2] * TOKENS_PER_NEO / 100000000

    # this would work for accepting gas
    # amount_requested = attachments.gas_attached * token.tokens_per_gas / 100000000

    exchange_ok = calculate_can_exchange(ctx, amount_requested, attachments[1], verify_only)

    return exchange_ok


def get_kyc_status(ctx, address):
    """
    Looks up the KYC status of an address

    :param address:bytearray The address to lookup
    :param storage:StorageAPI A StorageAPI object for storage interaction
    :return:
        bool: KYC Status of address
    """
    kyc_storage_key = concat(KYC_KEY, address)

    return Get(ctx, kyc_storage_key)


def calculate_can_exchange(ctx, amount, address, verify_only):
    """
    Perform custom token exchange calculations here.

    :param amount:int Number of tokens to convert from asset to tokens
    :param address:bytearray The address to mint the tokens to
    :return:
        bool: Whether or not an address can exchange a specified amount
    """
    height = GetHeight()

    current_in_circulation = Get(ctx, TOKEN_CIRC_KEY)

    new_amount = current_in_circulation + amount

    if new_amount > TOKEN_TOTAL_SUPPLY:
        return False

    if height < BLOCK_SALE_START:
        return False

    # if we are in free round, any amount
    if height > LIMITED_ROUND_END:
        return True

    # check amount in limited round
    if amount <= MAX_EXCHANGE_LIMITED_ROUND:

        # check if they have already exchanged in the limited round
        r1key = concat(address, LIMITED_ROUND_KEY)
        has_exchanged = Get(ctx, r1key)

        # if not, then save the exchange for limited round
        if not has_exchanged:
            # note that this method can be invoked during the Verification trigger, so we have the
            # verify_only param to avoid the Storage.Put during the read-only Verification trigger.
            # this works around a "method Neo.Storage.Put not found in ->" error in InteropService.py
            # since Verification is read-only and thus uses a StateReader, not a StateMachine
            if not verify_only:
                Put(ctx, r1key, True)
            return True

        return False

    return False
