from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.System.ExecutionEngine import GetExecutingScriptHash
from boa.blockchain.vm.Neo.Runtime import Notify,CheckWitness
from nex.token.mytoken import Token
from nex.common.storage import StorageAPI
from boa.code.builtins import range

OnTransfer = RegisterAction('transfer','from', 'to', 'amount')

class Airdrop():

    tokens_per_drop = 1


    def airdrop_tokens(self, args, token:Token):
        """

        :param args:list a list of addresses to airdrop to
        :param token:Token A token object with your ICO settings
        :return:
            int: The number of tokens dropped in this invocation
        """

        ok_count = 0

        if CheckWitness(token.owner):

            amount = len(args)

            storage = StorageAPI()

            current_in_circulation = storage.get(token.in_circulation_key)

            new_amount = current_in_circulation + amount 

            if new_amount > token.total_supply:
                print("Amount in list would overflow the total supply")
                return False

            sender = GetExecutingScriptHash()

            # Neo only supports 16 elements in an array, but by the time
            # you have 16 addresses in your invoke, you'll be in excess 
            # of 10 GAS anyway. 6 elements seems to work for < 10 GAS
            for address in args:
                if len(address) == 20:

                    storage.put(address, self.tokens_per_drop)

                    # dispatch transfer event
                    OnTransfer(sender, address, self.tokens_per_drop)
                    ok_count += self.tokens_per_drop

            # update the in circulation amount
            token.add_to_circulation(ok_count, storage)

        return ok_count

