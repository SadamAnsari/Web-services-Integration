#!/usr/bin/python

import logging
import requests
import json
import webservice.restclient
from requests.auth import HTTPBasicAuth
from utility import add_http

logger = logging.getLogger("Notification")


class ServiceNowFields(webservice.restclient.TrRestClient):
    def __init__(self, server_url, username, password):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   server_url, username))
        webservice.restclient.TrRestClient.__init__(self, server_url, username,
                                                    password)

        self.API_URL = add_http(server_url, is_secure=True)
        self.username = username
        self.password = password
        self.caller_ids = {}

    def get_auth_token(self):
        return HTTPBasicAuth(self.username, self.password)

    def get_url(self):
        return "%s/api/now/v2/table/sys_user" % self.API_URL

    def load_fields(self, search_name):
        self.fields = [self.get_caller_ids(search_name)]
        return self.fields

    def get_filter_url(self, filter_with):
        return "%s?sysparm_query=active=true^emailSTARTSWITH%s" % (self.get_url(), filter_with)

    def get_caller_ids(self, search_name):
        auth_token = self.get_auth_token()
        url = self.get_filter_url(search_name)
        headers = {"Accept": "application/json"}
        response = requests.get(url=url, auth=auth_token, headers=headers)
        logger.info("Method:GET, Response Code: %s, URL: %s" %
                    (response.status_code, url))
        if response.status_code != 200:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        else:
            data = json.loads(response._content)
            if len(data['result']) > 0:
                for i in range(len(data['result'])):
                    if data['result'][i]['sys_id'] is None:
                        continue
                    else:
                        self.caller_ids[i] = [data['result'][i]['sys_id'],data['result'][i]['email']]
            else:
                print "No records found. Search Again..."
        return self.caller_ids

    def get_field_label(self, tmp_dict, index, field, search_index):
        key = (key for key, value in tmp_dict.iteritems() if value[index] == field).next()
        return tmp_dict[key][search_index]