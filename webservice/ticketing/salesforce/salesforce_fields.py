#!/usr/bin/python

import beatbox
import logging
from collections import OrderedDict

logger = logging.getLogger("Notification")


class SalesForceFields:
    def __init__(self, server_url="", username="", password="", security_token=""):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   server_url, username))
        self.username = username
        self.password = password
        self.security_token = security_token
        self.service = beatbox.PythonClient()
        self.service.login(username, password + security_token)

        self.accounts = {}
        self.contacts = {}
        self.statuses = {}
        self.priorities = {}

    def load_fields(self):
        self.fields = [self.get_accounts(), self.get_status(), self.get_priority()]
        return self.fields

    def get_accounts(self):
        result_set = self.service.query("SELECT Id, Name from Account")
        if len(result_set) > 0:
            for account in range(len(result_set)):
                self.accounts[account] = [result_set[account]['Id'], result_set[account]['Name']]
            return self.accounts
        else:
            raise Exception("No Accounts found in SalesForce")

    def get_contacts(self, account_id):
        result_set = self.service.query("SELECT Id, Name from Contact WHERE AccountId='%s'" % account_id)
        if len(result_set) > 0:
            for contact in range(len(result_set)):
                self.contacts[contact] = [result_set[contact]['Id'], result_set[contact]['Name']]
            return self.contacts
        else:
            raise Exception("No Contacts found for the account_id: %s" % account_id)

    def get_status(self):
        status_object = self.service.describeSObjects('Case')
        status_field = status_object[0].fields['Status'].picklistValues
        if len(status_field) > 0:
            for index in range(len(status_field)):
                self.statuses[index] = [index, status_field[index]['value']]
            return self.statuses
        else:
            raise Exception("Status not found")

    def get_priority(self):
        priority_object = self.service.describeSObjects('Case')
        priority_field = priority_object[0].fields['Priority'].picklistValues
        if len(priority_field) > 0:
            for index in range(len(priority_field)):
                self.priorities[index] = [index, priority_field[index]['value']]
            return self.priorities
        else:
            raise Exception("Priority not found")