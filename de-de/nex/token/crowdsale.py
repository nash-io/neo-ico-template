from boa.blockchain.vm.Neo.Blockchain import GetHeight
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.Runtime import Notify,CheckWitness
from boa.code.builtins import concat
from nex.token.mytoken import Token
from nex.common.storage import StorageAPI
from nex.common.txio import Attachments,get_asset_attachments

OnTransfer = RegisterAction('transfer', 'to', 'from', 'amount')
OnRefund = RegisterAction('refund', 'to', 'amount')

OnInvalidKYCAddress = RegisterAction('invalid_registration','address')
OnKYCRegister = RegisterAction('kyc_registration','address')


class Crowdsale():

    kyc_key = b'kyc_ok'

    limited_round_key = b'r1'


    def kyc_register(self, args, token:Token):
        """

        :param args:List Eine Liste der Adressen die zu registrieren sind
        :param token:Token Ein Token Objekt mit Ihren ICO Einstellungen
        :return:
            int: Die Nummer der Adressen die mit KYC registriert werden
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
        Gibt den KYC Status einer Adresse aus

        :param args:list Eine Liste mit Argumenten
        :return:
            bool: Gibt den KYC Status einer Adresse aus
        """
        storage = StorageAPI()

        if len(args) > 0:
            addr = args[0]

            kyc_storage_key = concat(self.kyc_key, addr)

            return storage.get(kyc_storage_key)

        return False



    def exchange(self, token: Token):
        """

        :param token:Token Das Token Objekt mit NEP5/sale Einstellungen
        :return:
            bool: Ob der exchange erfolgreich war
        """

        attachments = get_asset_attachments()  # type:  Attachments

        storage = StorageAPI()

        # Dies überprüft ob der exchange ausgeführt werden kann
        can_exchange = self.can_exchange(token, attachments, storage)

        if not can_exchange:
            print("Cannot exchange value")
            # Dies sollte nur passieren im Fall das viele TX auf dem Final Block sind bevor 
            # der total amount erreicht ist. Nur eine Teilmenge der TX wird durch die Verification
            # Phase kommen und da die Gesamtmenge während dieser Phase nicht erhöht werden kann,
            # sollte es einen Prozess zur manuellen Erstattung der Tokens geben.
            OnRefund(attachments.sender_addr, attachments.neo_attached)
            return False


        # Suche den aktuellen Kontostand einer Adresse
        current_balance = storage.get(attachments.sender_addr)

        # Kalkuliere den Wert an Tokens die die angehängten NEO Wert sind
        exchanged_tokens = attachments.neo_attached * token.tokens_per_neo / 100000000

        # Wenn Sie anstatt Neo, Gas verwenden wollen benutzen Sie dies hier
        # exchanged_tokens += attachments.gas_attached * token.tokens_per_gas / 100000000


        # Fügen Sie die erhaltenen Tokens zu dem Persisten Storage hinzu
        new_total = exchanged_tokens + current_balance
        storage.put(attachments.sender_addr, new_total)

        # Updaten Sie den im Umlauf befindenden Wert 
        token.add_to_circulation(exchanged_tokens, storage)

        # Dispatch Transfer Event
        OnTransfer(attachments.receiver_addr, attachments.sender_addr, exchanged_tokens)

        return True


    def can_exchange(self, token:Token, attachments:Attachments, storage:StorageAPI) -> bool:
        """
       Legt fest ob der Contract Aufruf alle Voraussetzungen für den ICO exchange von NEO oder Gas in NEP5 Tokens erfüllt. 
       Anmerkung: Diese Methode kann sowohl über die Verification Portion oder die Application Portion 
       eines SC aufgerufen werden.

       Wenn in der Verification Portion eines SC aufgerufen, kann es benutzt werden um TX abzulehnen die
       nicht den Kriterien für den exchange entsprechen. Sodass der Aufwand für manuelle Erstattungen verringert wird.
       
        :param token:Token Ein Token Objekt mit Ihren ICO Einstellungen
        
        :param attachments:Attachments Ein Attachments Objekt mit Informationen über angehängte NEO/GAS Assets
        :param storage:StorageAPI Ein StorageAPI Objekt für Storage Interaktionen
        :return:
            bool: Ob eine Invocation den Vorrausetzungen eines exchange entspricht
        """

        # Wenn Sie Gas akzeptieren wollen, benutzen Sie folgendes
#        if attachments.gas_attached == 0:
#            print("no gas attached")
#            return False

        # Wenn Sie Neo akzeptieren wollen, benutzen Sie folgendes

        if attachments.neo_attached == 0:
            return False

        #  Das Folgende sucht ob eine Adresse für KYC Regulierungen
        #  registriert ist. Dies ist nicht für Operationen des Contract erforderlich.

        if not self.get_kyc_status(attachments.sender_addr, storage):
            return False

        print("Will check can exchange") # @TODO [Compiler FIX] removing this breaks the execution of this method

        # Kalkuliert den angeforderten Betrag 
        amount_requested = attachments.neo_attached * token.tokens_per_neo / 100000000
        # Folgendes funktioniert mit Gas 
        # amount_requested = attachments.gas_attached * token.tokens_per_gas / 100000000

        can_exchange = self.calculate_can_exchange(token, amount_requested, attachments.sender_addr)

        return can_exchange


    def get_kyc_status(self, address, storage:StorageAPI):
        """
        Überprüft den KYC Status einer Adresse

        :param address:bytearray Die zu durchsuchende Adresse
        :param storage:StorageAPI  Ein StorageAPI Objekt für Storage Interaktionen
        :return:
            bool: KYC Status der Adresse
        """
        kyc_storage_key = concat(self.kyc_key, address)

        return storage.get(kyc_storage_key)


    def calculate_can_exchange(self, token: Token, amount: int, address):
        """
        Führt benutzerdefinierte Token exchange Kalkulationen aus.

        :param token:Token Die Token Einstellungen für den Verkauf
        :param amount:int Nummer der Tokens die von Asset zu Tokens konvertiert werden
        :param address:bytearray Die Adresse wo die Tokens erzeugt werden sollen
        :return:
            bool: Ob eine Adresse einen bestimmten Betrag tauschen kann oder nicht
        """
        height = GetHeight()

        storage = StorageAPI()

        current_in_circulation = storage.get(token.in_circulation_key)

        new_amount = current_in_circulation + amount

        if new_amount > token.total_supply:
            # print("amount greater than total supply")
            return False

        if height < token.block_sale_start:
            # print("sale not begun yet")
            return False

        # Ob wir in einer freien Runde sind, jeder Betrag
        if height > token.limited_round_end:
            # print("Free for all, accept as much as possible")
            return True


        # Überprüfe Betrag in einer limitierten Runde

        if amount <= token.max_exchange_limited_round:

            # Überprüfe ob die Adresse bereits in einer limitierten Runde teilgenommen haben
            r1key = concat(address, self.limited_round_key)

            has_exchanged = storage.get(r1key)

            # falls nicht, dann sichere den exchange für die limitierte Runde
            if not has_exchanged:
                storage.put(r1key, True)
                return True

            print("already exchanged in limited round")
            return False

        print("too much for limited round")

        return False 
