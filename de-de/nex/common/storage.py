from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete


class StorageAPI():
    """
    Wrapper for the storage api
    """
    ctx = GetContext()

    def get(self, key):

        return Get(self.ctx, key)

    def put(self, key, value):

        Put(self.ctx, key, value)

    def delete(self, key):

        Delete(self.ctx, key)
