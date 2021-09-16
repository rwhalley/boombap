class Error(Exception):
    """Base class for other exceptions"""
    pass

class DeviceNotFound(Error):
    """Raised when device not found"""
    pass


