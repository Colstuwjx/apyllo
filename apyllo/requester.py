# coding=utf-8

import requests
import json
from .exceptions import RequestError, Request4xx5xxError


class WebClient(object):
    """
    base WebClient interface, implement the common things in web world.
    """
    def __init__(self, host, schema="http://", timeout=10, session=None):
        self.host = host
        self.schema = schema
        self.session = requests.Session() if session is None else session
        self.timeout = timeout

    def _do_request(
        self, method, path, params=None,
        data=None, timeout=None
    ):
        headers = {
            'Content-Type': 'application/json', 'Accept': 'application/json'}

        url = ''.join([self.schema, self.host.rstrip('/'), path])
        resp = self.session.request(
            method, url,
            params=params, data=data,
            headers=headers, timeout=(timeout or self.timeout)
        )

        if resp is None:
            exception = RequestError(server=self.host)
            raise exception

        if resp.status_code >= 200 and resp.status_code < 400:
            return resp
        else:
            exception = Request4xx5xxError(
                self.host, resp.text.encode('utf-8')
            )
            raise exception

    def __repr__(self):
        return 'Connection: %s' % self.host
