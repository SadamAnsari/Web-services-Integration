#!/usr/bin/python
import requests
import webservice.restclient
from requests.auth import HTTPBasicAuth
from utility import add_http
import logging

logger = logging.getLogger("Notification")


class FreshServiceFields(webservice.restclient.TrRestClient):
    def __init__(self, server_url, username, password):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   server_url, username))
        webservice.restclient.TrRestClient.__init__(self, server_url, username,
                                                    password)
        self.requesters = {}
        self.statuses = {}
        self.priorities = {}
        self.API_URL = add_http(server_url, is_secure=True)
        self.username = username
        self.password = password

    def get_requesters_url(self):
        return "%s/itil/requesters.json" % self.API_URL

    def get_ticket_fields_url(self):
        return "%s/ticket_fields.json" % self.API_URL

    def load_fields(self):
        self.fields = [self.load_requesters(), self.load_status(), self.load_priority()]
        return self.fields

    def get_auth_token(self):
        return HTTPBasicAuth(self.username, self.password)

    def load_requesters(self):
        auth_token = self.get_auth_token()
        url = self.get_requesters_url()
        response = requests.get(url, auth=auth_token)
        if response.status_code != 200:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        else:
            data = response.json()
            for users in range(len(data)):
                if data[users]['user']['active']:
                    self.requesters[data[users]['user']['id']] = data[users]['user']['email']
        return self.requesters

    def load_status(self):
        auth_token = self.get_auth_token()
        url = self.get_ticket_fields_url()
        response = requests.get(url, auth=auth_token)
        if response.status_code != 200:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        else:
            data = response.json()
            for item in range(len(data)):
                if data[item]['ticket_field']['label'] == 'Status':
                    self.statuses = self.convert_to_dict(data[item]['ticket_field']['choices'])
        return self.statuses

    def load_priority(self):
        auth_token = self.get_auth_token()
        url = self.get_ticket_fields_url()
        response = requests.get(url, auth=auth_token)
        if response.status_code != 200:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        else:
            data = response.json()
            for item in range(len(data)):
                if data[item]['ticket_field']['label'] == 'Priority':
                    self.priorities = self.convert_to_dict(data[item]['ticket_field']['choices'])
        return self.priorities

    def convert_to_dict(self, list):
        mydict = dict(list)
        mydict_new = {y: x for x, y in mydict.iteritems()}
        return mydict_new
