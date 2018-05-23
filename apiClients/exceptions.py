#!/usr/bin/python3.6

class GetAreaException(Exception):
    def __init__(self, *args, **kwrags):
        super(GetAreaException, self).__init__(*args, **kwrags)

class GetNetworkException(Exception):
    def __init__(self, *args, **kwrags):
        super(GetNetworkException, self).__init__(*args, **kwrags)

class CreateNetworkException(Exception):
    def __init__(self, *args, **kwrags):
        super(CreateNetworkException, self).__init__(*args, **kwrags)

class UpdateNetworkException(Exception):
    def __init__(self, *args, **kwrags):
        super(UpdateNetworkException, self).__init__(*args, **kwrags)

class DeleteNetworkException(Exception):
    def __init__(self, *args, **kwrags):
        super(DeleteNetworkException, self).__init__(*args, **kwrags)

class GetTemplateException(Exception):
    def __init__(self, *args, **kwrags):
        super(GetTemplateException, self).__init__(*args, **kwrags)

class GetVmException(Exception):
    def __init__(self, *args, **kwargs):
        super(GetVmException, self).__init__(*args, **kwargs)

class CreateVmException(Exception):
    def __init__(self, *args, **kwargs):
        super(CreateVmException, self).__init__(*args, **kwargs)

class UpdateVmException(Exception):
    def __init__(self, *args, **kwargs):
        super(UpdateVmException, self).__init__(*args, **kwargs)

class DeleteVmException(Exception):
    def __init__(self, *args, **kwargs):
        super(DeleteVmException, self).__init__(*args, **kwargs)

class GetRouterException(Exception):
    def __init__(self, *args, **kwargs):
        super(GetRouterException, self).__init__(*args, **kwargs)

class CreateRouterException(Exception):
    def __init__(self, *args, **kwargs):
        super(CreateRouterException, self).__init__(*args, **kwargs)

class UpdateRouterException(Exception):
    def __init__(self, *args, **kwargs):
        super(UpdateRouterException, self).__init__(*args, **kwargs)

class DeleteRouterException(Exception):
    def __init__(self, *args, **kwargs):
        super(DeleteRouterException, self).__init__(*args, **kwargs)

class GetIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super(GetIfaceException, self).__init__(*args, **kwargs)

class CreateIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super(CreateIfaceException, self).__init__(*args, **kwargs)

class UpdateIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super(UpdateIfaceException, self).__init__(*args, **kwargs)

class DeleteIfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super(DeleteIfaceException, self).__init__(*args, **kwargs)

class WrongTypeException(Exception):
    def __init__(self, *args, **kwargs):
        super(WrongTypeException, self).__init__(*args, **kwargs)