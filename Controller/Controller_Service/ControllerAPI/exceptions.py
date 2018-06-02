class APICallException(Exception):
    '''exception raised by retry decorator in case of failure calling an API'''
    def __init__(self, *args, **kwargs):
        super().__init__("Communication with InventoryAPI failed.")


class MethodNotSupportedException(Exception):
    '''exception raised by api_call helper function in case of passing wrong method type'''
    def __init__(self, *args, **kwargs):
        super().__init__("method not supported. Supported methods are ['post', 'get', 'put', 'delete']")


class MissingKeyException(Exception):
    '''raised when deserializing request body'''
    def __init__(self, *args, **kwargs):
        super().__init__(f"missing keys")