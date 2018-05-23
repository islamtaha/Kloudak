#!/usr/bin/python3.6

class CreateIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AddToBridgeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ConnectionFailedException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class BringIfaceUpException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GetIfaceMacException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateVolumeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteVolumeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StoragePoolMissingException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TemplateMissingException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateMetaDataException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateUserDataException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteMetaDataException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteUserDataException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class WrongTypeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateConfigIsoException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteConfigIsoException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateDirException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateVmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)