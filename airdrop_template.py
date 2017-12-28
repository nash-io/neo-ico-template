"""
NEP-5 Airdrop Template
===================================

Author: Joe Stewart
Email: joe@splyse.tech

Based on NEX NEP-5 ICO template by Thomas Saunders

Date: Dec 21 2017

"""

from boa.blockchain.vm.Neo.Runtime import GetTrigger, CheckWitness, Notify
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from nex.common.storage import StorageAPI
from nex.token.mytoken import Token
from nex.token.nep5 import NEP5Handler
from nex.token.airdrop import Airdrop

OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnRedeem = RegisterAction('redeem', 'addr_from', 'amount')

def Main(operation, args):
    """

    :param operation: str The name of the operation to perform
    :param args: list A list of arguments along with the operation
    :return:
        bytearray: The result of the operation
    """

    trigger = GetTrigger()
    token = Token()

    #print("Executing Airdrop Template")

    # This is used in the Verification portion of the contract
    # To determine whether a transfer of system assets ( NEO/Gas) involving
    # This contract's address can proceed
    if trigger == Verification:

        # check if the invoker is the owner of this contract
        is_owner = CheckWitness(token.owner)

        # If owner, proceed
        if is_owner:

            return True

        # Normally we'd check attachments and crowdsale rules
        # but this is an airdrop - no funds should ever be sent,
        # so reject any that are

        return False


    elif trigger == Application:

        if operation != None:

            # take a list of address scripthashes and assign tokens to them
            # this operation should always be first checked in order to 
            # conserve GAS usage, allowing more addresses to be airdropped 
            # tokens to per invocation of the contract

            if operation == 'airdropTokens':
                drop = Airdrop()
                return drop.airdrop_tokens(args, token)

            nep = NEP5Handler()

            for op in nep.get_methods():
                if operation == op:
                    return nep.handle_nep51(operation, args, token)

            if operation == 'deploy':
                return deploy(token)

            if operation == 'circulation':
                storage = StorageAPI()
                return token.get_circulation(storage)

            # how many tokens have been redeemed/burned by all holders
            # subtract from circulation to get true amount of active
            # tokens left in the contract
           
            if operation == 'redeemed':
                storage = StorageAPI()
                return storage.get("redeemed")

            # normal crowdsale operations don't apply in an airdrop
            # so we will just return False/0 for those
 
            if operation == 'mintTokens':
                return False

            if operation == 'crowdsale_register':
                return False

            if operation == 'crowdsale_status':
                return False

            if operation == 'crowdsale_available':
                return 0

            # special function needed by future non-fungible token contract 
            # to trade fungible tokens in this contract for non-fungible 
            # tokens in that contract
    
            if operation == 'redeemTokens':

                if len(args) == 2:
                    t_from = args[0]
                    t_amount = args[1]
                    return redeem(t_from, t_amount)
                return False

            return 'unknown operation'

    return False


def deploy(token: Token):
    """

    :param token: Token The token to deploy
    :return:
        bool: Whether the operation was successful
    """
    if not CheckWitness(token.owner):
        print("Must be owner to deploy")
        return False

    storage = StorageAPI()

    if not storage.get('initialized'):

        # do deploy logic
        storage.put('initialized', 1)
        storage.put(token.owner, token.initial_amount)
        token.add_to_circulation(token.initial_amount, storage)

        return True

    return False


def redeem(t_from, amount):

    """
    Tokens redeemed here will disappear from the invoker's account
    but the total in circulation will not be changed. To find out
    how many have been redeemed so far call the redeemed() operation
    """

    if amount <= 0:
        return False

    storage = StorageAPI()

    if CheckWitness(t_from):

        from_val = storage.get(t_from)

        if from_val < amount:
            print("insufficient funds")
            return False

        if from_val == amount:
            storage.delete(t_from)

        else:
            difference = from_val - amount
            storage.put(t_from, difference)

        last_redeemed_count = storage.get('redeemed')
        new_redeemed_count = last_redeemed_count + amount
        storage.put('redeemed', new_redeemed_count)

        # Notification to redemption handling backend

        OnRedeem(t_from, amount)

        # Need to emit a Transfer message with null destination 
        # address for blockchain explorers to know that the address
        # token balance has changed due to being redeemed

        OnTransfer(t_from, None, amount)

        return True
    else:
        print("from address is not the tx sender")

    return False

