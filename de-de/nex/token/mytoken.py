from nex.common.storage import StorageAPI

class Token():
    """
    Basiseinstellungen für einen NEP5 Token und den Crowdsale
    """

    name = 'NEX Template'

    symbol = 'NXT'

    decimals = 8

    # Dies ist der Script Hash der Adresse des Tokenowners
    # Dies kann in ``neo-python``gefunden werden. Mit einem offenen Wallet benutzen Sie das ``wallet`` Kommando
    owner = b'\xaf\x12\xa8h{\x14\x94\x8b\xc4\xa0\x08\x12\x8aU\nci[\xc1\xa5'

    in_circulation_key = b'in_circulation'

    total_supply = 10000000 * 100000000  # 10m total supply * 10^8 ( decimals)

    initial_amount = 2500000 * 100000000  # 2.5m to owners * 10^8

    # Nehmen Sie an 1 Dollar pro Token, und ein Neo = 40 dollars * 10^8
    tokens_per_neo = 40 * 100000000

    # Nehmen Sie an 1 Dollar pro Token, und ein Gas = 20 dollars * 10^8
    tokens_per_gas = 20 * 100000000


    # Maximaler Betrag den Sie in der limitierten Runde erzeugen können ( 500 neo times 40 per neo * 10^8 )
    max_exchange_limited_round = 500 * 40 * 100000000

    # Wann der Crowdsale startet
    block_sale_start = 875000

    # Wann die initiale limitierte Runde endet
    limited_round_end = 875000 + 10000



    def crowdsale_available_amount(self):
        """

        :return: int Der Betrag der Tokens der für den Crowdsale Verkauf übrig ist
        """
        storage = StorageAPI()

        in_circ = storage.get(self.in_circulation_key)

        available = self.total_supply - in_circ

        return available


    def add_to_circulation(self, amount:int, storage:StorageAPI):
        """
        Addiert einen Betrag an Tokens zu den Tokens im Umlauf

        :param amount: int Der Betrag der zu den Tokens im Umlauf addiert werden soll
        :param storage:StorageAPI Ein StorageAPI Objekt für storage Interaktionen
        """
        current_supply = storage.get(self.in_circulation_key)

        current_supply += amount

        storage.put(self.in_circulation_key, current_supply)



    def get_circulation(self, storage:StorageAPI):
        """
        Gibt den Gesamtbetrag der Tokens im Umlauf zurück

        :param storage:StorageAPI Ein StorageAPI Objekt für storage Interaktionen
        :return:
            int: Gesamtbetrag im Umlauf
        """
        return storage.get(self.in_circulation_key)

