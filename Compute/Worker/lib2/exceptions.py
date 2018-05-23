#!/usr/bin/python3.6

class CreateAreaException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteAreaException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UpdateAreaException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateHostException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteHostException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UpdateHostException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreatePoolException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeletePoolException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UpdatePoolException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UpdateIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GetIfaceMacException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AddToBridgeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class BringIfaceUpException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class WrongTypeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ConnectionFailedException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateDirException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteDirException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StoragePoolMissingException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TemplateMissingException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateVolumeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteVolumeException(Exception):
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

class CreateConfigIsoException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteConfigIsoException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CreateVmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeleteVmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UpdateVmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
