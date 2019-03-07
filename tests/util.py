import os
import hashlib
import tempfile

from apiclient.discovery import build

# To workaround the `file_cache is unavailable when using oauth2client >= 4.0.0
# or google-auth` error, use our own cache for google's discovery documents
# https://github.com/googleapis/google-api-python-client/issues/325#issuecomment-419387788
class DiscoveryCache:
    def filename(self, url):
        return os.path.join(
            tempfile.gettempdir(),
            'google_api_discovery_' + hashlib.md5(url.encode()).hexdigest())

    def get(self, url):
        try:
            with open(self.filename(url), 'rb') as f:
                return f.read().decode()
        except FileNotFoundError:
            return None

    def set(self, url, content):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content.encode())
            f.flush()
            os.fsync(f)
        os.rename(f.name, self.filename(url))

def load_test_data(file_name):
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

    full_name = os.path.join(DATA_DIR, file_name)
    with open(full_name) as f:
        doc = f.read()
    return doc

discovery_cache = DiscoveryCache()
build('bigquery','v2', cache=discovery_cache)
build('compute','v1', cache=discovery_cache)
build('sqladmin','v1beta4', cache=discovery_cache)
build('storage','v1', cache=discovery_cache)
