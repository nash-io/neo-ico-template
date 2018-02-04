from boa.blockchain.vm.Neo.Runtime import CheckWitness, Notify
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.code.builtins import concat

from nex.token.mytoken import Token
from nex.common.storage import StorageAPI


OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnApprove = RegisterAction('approve', 'addr_from', 'addr_to', 'amount')


class NEP5Handler():

    def get_methods(self):

        m = ['name', 'symbol', 'decimals', 'totalSupply', 'balanceOf','transfer', 'transferFrom', 'approve', 'allowance']
        return m

    def handle_nep51(self, operation, args, token: Token):

        # these first 3 don't require get ctx

        if operation == 'name':
            return token.name

        elif operation == 'decimals':
            return token.decimals

        elif operation == 'symbol':
            return token.symbol

        storage = StorageAPI()

        arg_error = 'Incorrect Arg Length'

        if operation == 'totalSupply':
            return storage.get(token.in_circulation_key)

        elif operation == 'balanceOf':
            if len(args) == 1:
                account = args[0]
                return storage.get(account)
            return arg_error

        elif operation == 'transfer':
            if len(args) == 3:
                t_from = args[0]
                t_to = args[1]
                t_amount = args[2]
                return self.do_transfer(storage, t_from, t_to, t_amount)
            return arg_error

        elif operation == 'transferFrom':
            if len(args) == 3:
                t_from = args[0]
                t_to = args[1]
                t_amount = args[2]
                return self.do_transfer_from(storage, t_from, t_to, t_amount)
            return arg_error

        elif operation == 'approve':
            if len(args) == 3:
                t_owner = args[0]
                t_spender = args[1]
                t_amount = args[2]
                return self.do_approve(storage, t_owner, t_spender, t_amount)
            return arg_error

        elif operation == 'allowance':
            if len(args) == 2:
                t_owner = args[0]
                t_spender = args[1]
                return self.do_allowance(storage, t_owner, t_spender)

            return arg_error

        return False

    def do_transfer(self, storage: StorageAPI, t_from, t_to, amount):

        if amount <= 0:
            return False

        if len(t_to) != 20:
            return False

        if CheckWitness(t_from):

            if t_from == t_to:
                print("transfer to self!")
                return True

            from_val = storage.get(t_from)

            if from_val < amount:
                print("insufficient funds")
                return False

            if from_val == amount:
                storage.delete(t_from)

            else:
                difference = from_val - amount
                storage.put(t_from, difference)

            to_value = storage.get(t_to)

            to_total = to_value + amount

            storage.put(t_to, to_total)

            OnTransfer(t_from, t_to, amount)

            return True
        else:
            print("from address is not the tx sender")

        return False

    def do_transfer_from(self, storage: StorageAPI, t_from, t_to, amount):

        if amount <= 0:
            return False

        available_key = concat(t_from, t_to)

        if len(available_key) != 40:
            return False

        available_to_to_addr = storage.get(available_key)

        if available_to_to_addr < amount:
            print("Insufficient funds approved")
            return False

        from_balance = storage.get(t_from)

        if from_balance < amount:
            print("Insufficient tokens in from balance")
            return False

        to_balance = storage.get(t_to)

        new_from_balance = from_balance - amount

        new_to_balance = to_balance + amount

        storage.put(t_to, new_to_balance)
        storage.put(t_from, new_from_balance)

        print("transfer complete")

        new_allowance = available_to_to_addr - amount

        if new_allowance == 0:
            print("removing all balance")
            storage.delete(available_key)
        else:
            print("updating allowance to new allowance")
            storage.put(available_key, new_allowance)

        OnTransfer(t_from, t_to, amount)

        return True

    def do_approve(self, storage: StorageAPI, t_owner, t_spender, amount):

        if not CheckWitness(t_owner):
            print("Incorrect permission")
            return False

        if amount < 0:
            print("Negative amount")
            return False

        from_balance = storage.get(t_owner)

        # cannot approve an amount that is
        # currently greater than the from balance
        if from_balance >= amount:

            approval_key = concat(t_owner, t_spender)

            if amount == 0:
                storage.delete(approval_key)
            else:
                storage.put(approval_key, amount)

            OnApprove(t_owner, t_spender, amount)

            return True

        return False

    def do_allowance(self, storage: StorageAPI, t_owner, t_spender):

        allowance_key = concat(t_owner, t_spender)

        amount = storage.get(allowance_key)

        return amount
