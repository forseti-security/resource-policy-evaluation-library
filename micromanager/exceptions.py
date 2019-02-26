from googleapiclient.errors import HttpError


def is_retryable_exception(err):
    print(err)

    if isinstance(err, HttpError):
        return err.resp.status in [409]
