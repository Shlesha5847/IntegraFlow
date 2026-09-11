class VendorIntegrationException(Exception):
    """Raised when an external vendor integration fails (REST or SOAP)."""
    pass

class ResourceNotFoundException(Exception):
    """Raised when an entity is not found."""
    pass

class DuplicateResourceException(Exception):
    """Raised when unique constraint (e.g. email) is violated."""
    pass
