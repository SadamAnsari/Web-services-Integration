#!/usr/bin/python

# soapclient.py - REST client class, part of BlackStratus.

"""
    Top level access to REST service.
"""

import logging
import requests
from requests.auth import HTTPBasicAuth
logger = logging.getLogger("Notification")


class TrRestClient():
    def __init__(self, server_url, username, password):
        self.url = server_url
        self.username = username
        self.password = password

    def get_auth_token(self):
        return HTTPBasicAuth(self.username, self.password)

    def get(self, url, response_code=200):
        auth_token = self.get_auth_token()
        headers = {"Accept": "application/json"}
        response = requests.get(url=url, auth=auth_token, headers=headers)
        logger.info("Method:GET, Response Code: %s, URL: %s" %
                    (response.status_code, url))
        if response.status_code != response_code:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        return response.json()

    def post(self, url, data, response_code=200):
        auth_token = self.get_auth_token()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(url=url, auth=auth_token, data=data, headers=headers)
        logger.info("Method:POST, Response Code: %s, URL: %s" %
                    (response.status_code, url))
        if response.status_code != response_code:
            logger.error("Failed to post data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:POST, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        return response.json()

    def put(self, url, data, response_code=200):
        auth_token = self.get_auth_token()
        headers = {"Content-Type": "application/json"}
        response = requests.put(url=url, auth=auth_token, data=data, headers=headers)
        logger.info("Method:PUT, Response Code: %s, URL: %s" %
                    (response.status_code, url))
        if response.status_code != response_code:
            logger.error("Failed to update data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:PUT, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        return response.json()