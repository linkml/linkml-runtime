class OrderingError(RuntimeError):
    """Exception raised when there is a problem with SchemaView ordering"""


class AmbiguousNameError(RuntimeError):
    """Exception raised in the case of an ambiguous element name"""


class MissingElementError(RuntimeError):
    """Exception raised when an element is missing"""
