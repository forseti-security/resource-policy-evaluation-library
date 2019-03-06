from googleapiclient.errors import HttpError
from urllib.error import URLError


def is_retryable_exception(err):
    """
    Args:
        err: An exception

    Returns:
        True if the exception should trigger a retry of certain operations

    """
    if isinstance(err, HttpError):
        return err.resp.status in [409]

    if isinstance(err, URLError):
        return not isinstance(err, NoSuchEndpoint)

    return False


class NoSuchEndpoint(URLError):
    pass
