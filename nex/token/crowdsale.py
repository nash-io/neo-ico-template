from boa.blockchain.vm.Neo.Blockchain import GetHeight
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.Runtime import Notify,CheckWitness
from boa.code.builtins import concat
from nex.token.mytoken import Token
from nex.common.storage import StorageAPI
from nex.common.txio import Attachments,get_asset_attachments

OnTransfer = RegisterAction('transfer', 'from', 'to', 'amount')
OnRefund = RegisterAction('refund', 'to', 'amount')

OnInvalidKYCAddress = RegisterAction('invalid_registration','address')
OnKYCRegister = RegisterAction('kyc_registration','address')


class Crowdsale():

    kyc_key = b'kyc_ok'

    limited_round_key = b'r1'


    def kyc_register(self, args, token:Token):
        """

        :param args:list a list of addresses to register
        :param token:Token A token object with your ICO settings
        :return:
            int: The number of addresses to register for KYC
        """
        ok_count = 0

        if CheckWitness(token.owner):

            for address in args:

                if len(address) == 20:

                    storage = StorageAPI()

                    kyc_storage_key = concat(self.kyc_key, address)
                    storage.put(kyc_storage_key, True)

                    OnKYCRegister(address)
                    ok_count += 1

        return ok_count


    def kyc_status(self, args):
        """
        Gets the KYC Status of an address

        :param args:list a list of arguments
        :return:
            bool: Returns the kyc status of an address
        """
        storage = StorageAPI()

        if len(args) > 0:
            addr = args[0]

            kyc_storage_key = concat(self.kyc_key, addr)

            return storage.get(kyc_storage_key)

        return False



    def exchange(self, token: Token):
        """

        :param token:Token The token object with NEP5/sale settings
        :return:
            bool: Whether the exchange was successful
        """

        attachments = get_asset_attachments()  # type:  Attachments

        storage = StorageAPI()

        # this looks up whether the exchange can proceed
        can_exchange = self.can_exchange(token, attachments, storage, False)

        if not can_exchange:
            print("Cannot exchange value")
            # This should only happen in the case that there are a lot of TX on the final
            # block before the total amount is reached.  An amount of TX will get through
            # the verification phase because the total amount cannot be updated during that phase
            # because of this, there should be a process in place to manually refund tokens
            if attachments.neo_attached > 0:
                OnRefund(attachments.sender_addr, attachments.neo_attached)
            # if you want to exchange gas instead of neo, use this
            #if attachments.gas_attached > 0:
            #    OnRefund(attachments.sender_addr, attachments.gas_attached)
            return False


        # lookup the current balance of the address
        current_balance = storage.get(attachments.sender_addr)

        # calculate the amount of tokens the attached neo will earn
        exchanged_tokens = attachments.neo_attached * token.tokens_per_neo / 100000000

        # if you want to exchange gas instead of neo, use this
        # exchanged_tokens += attachments.gas_attached * token.tokens_per_gas / 100000000


        # add it to the the exchanged tokens and persist in storage
        new_total = exchanged_tokens + current_balance
        storage.put(attachments.sender_addr, new_total)

        # update the in circulation amount
        token.add_to_circulation(exchanged_tokens, storage)

        # dispatch transfer event
        OnTransfer(attachments.receiver_addr, attachments.sender_addr, exchanged_tokens)

        return True


    def can_exchange(self, token:Token, attachments:Attachments, storage:StorageAPI, verify_only: bool) -> bool:
        """
        Determines if the contract invocation meets all requirements for the ICO exchange
        of neo or gas into NEP5 Tokens.
        Note: This method can be called via both the Verification portion of an SC or the Application portion

        When called in the Verification portion of an SC, it can be used to reject TX that do not qualify
        for exchange, thereby reducing the need for manual NEO or GAS refunds considerably

        :param token:Token A token object with your ICO settings
        :param attachments:Attachments An attachments object with information about attached NEO/Gas assets
        :param storage:StorageAPI A StorageAPI object for storage interaction
        :return:
            bool: Whether an invocation meets requirements for exchange
        """

        # if you are accepting gas, use this
#        if attachments.gas_attached == 0:
#            print("no gas attached")
#            return False

        # if youre accepting neo, use this

        if attachments.neo_attached == 0:
            return False

        # the following looks up whether an address has been
        # registered with the contract for KYC regulations
        # this is not required for operation of the contract

#        status = self.get_kyc_status(attachments.sender_addr, storage)
        if not self.get_kyc_status(attachments.sender_addr, storage):
            return False

#        print("Will check can exchange") # @TODO [Compiler FIX] removing this print statement breaks the execution of this method in v 0.2.0 and below
#                                           @TODO Fixed in version 0.2.1


        # caluclate the amount requested
        amount_requested = attachments.neo_attached * token.tokens_per_neo / 100000000

        # this would work for accepting gas
        # amount_requested = attachments.gas_attached * token.tokens_per_gas / 100000000

        can_exchange = self.calculate_can_exchange(token, amount_requested, attachments.sender_addr, verify_only)

        return can_exchange


    def get_kyc_status(self, address, storage:StorageAPI):
        """
        Looks up the KYC status of an address

        :param address:bytearray The address to lookup
        :param storage:StorageAPI A StorageAPI object for storage interaction
        :return:
            bool: KYC Status of address
        """
        kyc_storage_key = concat(self.kyc_key, address)

        return storage.get(kyc_storage_key)


    def calculate_can_exchange(self, token: Token, amount: int, address, verify_only: bool):
        """
        Perform custom token exchange calculations here.

        :param token:Token The token settings for the sale
        :param amount:int Number of tokens to convert from asset to tokens
        :param address:bytearray The address to mint the tokens to
        :return:
            bool: Whether or not an address can exchange a specified amount
        """
        height = GetHeight()

        storage = StorageAPI()

        current_in_circulation = storage.get(token.in_circulation_key)

        new_amount = current_in_circulation + amount

        if new_amount > token.total_supply:
            print("amount greater than total supply")
            return False

        print("trying to calculate height????")
        if height < token.block_sale_start:
            print("sale not begun yet")
            return False

        # if we are in free round, any amount
        if height > token.limited_round_end:
            print("Free for all, accept as much as possible")
            return True


        # check amount in limited round

        if amount <= token.max_exchange_limited_round:

            # check if they have already exchanged in the limited round
            r1key = concat(address, self.limited_round_key)

            has_exchanged = storage.get(r1key)

            # if not, then save the exchange for limited round
            if not has_exchanged:
                # note that this method can be invoked during the Verification trigger, so we have the
                # verify_only param to avoid the Storage.Put during the read-only Verification trigger.
                # this works around a "method Neo.Storage.Put not found in ->" error in InteropService.py
                # since Verification is read-only and thus uses a StateReader, not a StateMachine
                if not verify_only:
                    storage.put(r1key, True)
                return True

            print("already exchanged in limited round")
            return False

        print("too much for limited round")

        return False
