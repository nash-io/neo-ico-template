"""
NEX ICO Vorlage
===================================

Author: Thomas Saunders
Email: tom@neonexchange.org

Date: Dec 11 2017

"""

from boa.blockchain.vm.Neo.Runtime import GetTrigger, CheckWitness, Notify
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from nex.common.storage import StorageAPI
from nex.common.txio import Attachments,get_asset_attachments
from nex.token.mytoken import Token
from nex.token.nep5 import NEP5Handler
from nex.token.crowdsale import Crowdsale


def Main(operation, args):
    """

    :param operation: str Der Name der Aufgabe die ausgeführt werden soll
    :param args: list Eine Liste der Argumente für die Ausführung
    :return:
        bytearray: Das Ergebnis der Ausführung
    """

    trigger = GetTrigger()
    token = Token()

    #print("Executing ICO Template")

    # Dies wird in der Verification portion des Contract benutzt
    # um festzustellen ob ein Transfer System Assets ( NEO/GAS) beinhaltet.
    # Diese Contract´s Adresse kann fortfahren
    if trigger == Verification:
        
        # Überprüfen Sie ob die aufrufende Instanz der Besitzer des Contracs ist
        is_owner = CheckWitness(token.owner)

        # Wenn Besitzer, fortfahren
        if is_owner:

            return True

        # Andernfalls, müssen Sie einen Lookup der Adresse machen und feststellen
        # ob der Anhang des Assets okay ist
        attachments = get_asset_attachments()  # type:Attachments

        storage = StorageAPI()

        crowdsale = Crowdsale()

        return crowdsale.can_exchange(token, attachments, storage)


    elif trigger == Application:

        if operation != None:

            nep = NEP5Handler()

            for op in nep.get_methods():
                if operation == op:
                    return nep.handle_nep51(operation, args, token)

            if operation == 'deploy':
                return deploy(token)

            if operation == 'circulation':
                storage = StorageAPI()
                return token.get_circulation(storage)

            # Das folgende wird von Crowdsale verarbeitet

            sale = Crowdsale()

            if operation == 'mintTokens':
                return sale.exchange(token)

            if operation == 'crowdsale_register':
                return sale.kyc_register(args, token)

            if operation == 'crowdsale_status':
                return sale.kyc_status(args)

            if operation == 'crowdsale_available':
                return token.crowdsale_available_amount()

            return 'unknown operation'

    return False


def deploy(token: Token):
    """

    :param token: Token Der Token der implementiert wird
    :return:
        bool: Ob die Ausführung erfolgreich war
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



