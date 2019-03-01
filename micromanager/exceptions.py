from googleapiclient.errors import HttpError


def is_retryable_exception(err):
    """
    Args:
        err: An exception

    Returns:
        True if the exception should trigger a retry of certain operations

    """
    if isinstance(err, HttpError):
        return err.resp.status in [409]

    return False
