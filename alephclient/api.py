import os
from six.moves.urllib.parse import urlencode
import requests


class AlephAPI(object):
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def _make_url(self, path, query=None, filters=None, **kwargs):
        params = kwargs
        if query:
            params["q"] = query
        if filters:
            for key, val in filters:
                params["filter:"+key] = val
        return self.base_url + path + '?' + urlencode(params)

    def _request(self, method, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = "ApiKey " + self.api_key
        response = requests.request(
                method=method, url=url, headers=headers, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_collection(self, collection_id):
        url = self._make_url("collections/{0}".format(collection_id))
        return self._request("GET", url)

    def filter_collections(self, query=None, filters=None, **kwargs):
        """Filter collections for the given query and/or filters.

        params
        ------
        query: query string
        filters: list of key, value pairs to filter collections
        kwargs: extra arguments for api call such as page, limit etc
        """
        if not query and not filters:
            raise ValueError("One of query or filters is required")
        url = self._make_url("collections", filters=filters, **kwargs)
        print(url)
        return self._request("GET", url)["results"]

    def create_collection(self, data):
        url = self._make_url("collections")
        print(data)
        return self._request("POST", url, data=data)

    def update_collection(self, collection_id, data):
        url = self._make_url("collections/{0}".format(collection_id))
        return self._request("PUT", url, data=data)

    def ingest_upload(self, collection_id, full_file_path, relative_file_path):
        url = self._make_url("collections/{0}/ingest".format(collection_id))
        path = os.path.abspath(os.path.normpath(full_file_path))
        if not os.path.isfile(path):
            raise ValueError("{0} is not a valid file path".format(path))
        with open(path, "rb") as fh:
            print("Uploading " + path)
            return self._request("POST", url, files={relative_file_path: fh})
