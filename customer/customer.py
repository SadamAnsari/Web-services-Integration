#!/usr/bin/python

import logging
from extrainfo import (AutoTaskInfo, JiraInfo, ConnectWiseInfo,
                       FreshServiceInfo, SalesForceInfo, ServiceNowInfo)

TICKETING_API_UNKNOWN = 0
TICKETING_API_AUTOTASK = 1
TICKETING_API_JIRA = 2
TICKETING_API_CONNECTWISE = 3
TICKETING_API_FRESHSERVICE = 4
TICKETING_API_SALESFORCE = 5
TICKETING_API_SERVICENOW = 6

TICKET_API = {
    TICKETING_API_UNKNOWN: "Unknown",
    TICKETING_API_AUTOTASK: "AutoTask",
    TICKETING_API_JIRA: "Jira",
    TICKETING_API_CONNECTWISE: "ConnectWise",
    TICKETING_API_FRESHSERVICE: "FreshService",
    TICKETING_API_SALESFORCE: "SalesForce",
    TICKETING_API_SERVICENOW: "ServiceNow"
}
logger = logging.getLogger("Notification")


class Customer:
    WILDCARD = "*"

    def __init__(self):
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.id = ""
        self.name = ""
        self.url = ""
        self.username = ""
        self.password = ""
        self.ticket_api = 0
        self.extra_info = None

    def get_api_id(self, api):
        """ In case ticket_api is having different convention then we need to do mapping here """
        api_id = api
        if api_id not in TICKET_API.keys():
            return UNKNOWN_API
        return api_id

    def set_ticketing_api(self, ticket_api):
        if self.ticket_api == ticket_api:
            return
        self.ticket_api = ticket_api
        if self.ticket_api == TICKETING_API_AUTOTASK:
            self.extra_info = AutoTaskInfo()
        elif self.ticket_api == TICKETING_API_JIRA:
            self.extra_info = JiraInfo()
        elif self.ticket_api == TICKETING_API_CONNECTWISE:
            self.extra_info = ConnectWiseInfo()
        elif self.ticket_api == TICKETING_API_FRESHSERVICE:
            self.extra_info = FreshServiceInfo()
        elif self.ticket_api == TICKETING_API_SALESFORCE:
            self.extra_info = SalesForceInfo()
        elif self.ticket_api == TICKETING_API_SERVICENOW:
            self.extra_info = ServiceNowInfo()

    def set(self, id, url, username, password, ticket_api, extra_info):
        logger.info("Setting customer info. Id:%s, url:%s, user:%s, ticketing API:%s, Extra_Info:%s" %
                    (id, url, username, ticket_api, extra_info))
        self.id = id
        self.url = url
        self.username = username
        self.password = password
        self.ticket_api = ticket_api
        if self.ticket_api == TICKETING_API_AUTOTASK:
            self.extra_info = AutoTaskInfo()
        elif self.ticket_api == TICKETING_API_JIRA:
            self.extra_info = JiraInfo()
        elif self.ticket_api == TICKETING_API_CONNECTWISE:
            self.extra_info = ConnectWiseInfo()
        elif self.ticket_api == TICKETING_API_FRESHSERVICE:
            self.extra_info = FreshServiceInfo()
        elif self.ticket_api == TICKETING_API_SALESFORCE:
            self.extra_info = SalesForceInfo()
        elif self.ticket_api == TICKETING_API_SERVICENOW:
            self.extra_info = ServiceNowInfo()
        self.extra_info.parse_extra_info(extra_info)

    def parse_connectwise_extra_info(self, extra_info):
        raise Exception("parse_connectwise_extra_info not Implemented")

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen == True:
            print("Customer Id: %s\nTicketing URL: %s\nUserName: %s\nTicketing Method: %s" %
                  (self.id, self.url, self.username, TICKET_API[self.ticket_api]))
        else:
            logger.info("Customer Information. Id: %s, URL: %s, UserName: %s, Ticket API: %s" %
                        (self.id, self.url, self.username, TICKET_API[self.ticket_api]))
        self.extra_info.print_info(on_screen, autotask_fields=autotask_fields)
