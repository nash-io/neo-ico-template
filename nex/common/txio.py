from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash


class Attachments():
    """
    Container object ( struct ) for passing around information about attached neo and gas
    """
    neo_attached, gas_attached = 0, 0
    
    sender_addr, receiver_addr = None, None

    neo_asset_id = b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5'

    gas_asset_id = b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`'


def get_asset_attachments() -> Attachments:
    """
    Gets information about NEO and Gas attached to an invocation TX

    :return:
        Attachments: An object with information about attached neo and gas
    """
    attachment = Attachments()
    attachment.receiver_addr = GetExecutingScriptHash()
    
    tx = GetScriptContainer()  # type:Transaction
    references = tx.References
    
    if len(references):

        reference = references[0]
        
        attachment.sender_addr = reference.ScriptHash

        for output in tx.Outputs:
            
            if output.ScriptHash == attachment.receiver_addr:
                
                if output.AssetId == attachment.neo_asset_id:
                    attachment.neo_attached += output.Value

                if output.AssetId == attachment.gas_asset_id:
                    attachment.gas_attached += output.Value


    return attachment
