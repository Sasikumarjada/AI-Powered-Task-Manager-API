class TaskNotFoundError(Exception):
    """Raised when a task is not found in the database"""
    pass


class ExternalAPIError(Exception):
    """Raised when external API call fails"""
    pass
