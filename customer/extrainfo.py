#!/usr/bin/python

import logging
import re


logger = logging.getLogger("Notification")

def get_label(input_dict, index, search_value, get_value=False):
    # print input_dict
    key = (key for key, value in input_dict.iteritems() if value[index] == search_value).next()
    if get_value:
        return input_dict[key][1]
    else:
        return key

class ExtraInfo(object):
    def __init__(self):
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.priority = -1
        self.account_id = -1

class JiraInfo(ExtraInfo):
    def __init__(self):
        super(JiraInfo, self).__init__()
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.issuetype = ""

    def get_info(self):
        return ("<j_issuetype:%s><j_priority:%s><j_account_id:%s>" %
                (self.issuetype, self.priority, self.account_id))

    def parse_extra_info(self, extra_info):
        logger.info("Parsing extra information. %s" % extra_info)
        matches = re.match("<j_issuetype:(.*?)><j_priority:(.*?)><j_account_id:(\S+)>",
                           extra_info, re.IGNORECASE)
        if matches:
            self.issuetype = matches.group(1)
            self.priority = matches.group(2)
            self.account_id = matches.group(3)

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen is True:
            print("Jira Issue Type: %s\nJira Ticket Priority : %s\nJira Project Name : %s" %
                  (self.issuetype, self.priority, self.account_id))
        else:
            logger.info("Jira Issue Type: %s, Jira Ticket Priority : %s, Jira Project Name : %s" %
                        (self.issuetype, self.priority, self.account_id))


class AutoTaskInfo(ExtraInfo):
    def __init__(self):
        super(AutoTaskInfo, self).__init__()
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.queue_id = -1
        self.status = -1

    def get_info(self):
        return ("<at_status:%s><at_priority:%s><at_queue_id:%s><at_account_id:%s>" %
                (self.status, self.priority, self.queue_id, self.account_id))

    def parse_extra_info(self, extra_info):
        logger.info("Parsing extra information. %s" % extra_info)
        matches = re.match("<at_status:(\d+)><at_priority:(\d+)><at_queue_id:(\d+)><at_account_id:(\d+)>",
                           extra_info, re.IGNORECASE)
        if matches:
            self.status = int(matches.group(1))
            self.priority = int(matches.group(2))
            self.queue_id = int(matches.group(3))
            self.account_id = int(matches.group(4))

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen is True:
            if (autotask_fields is not None):
                print(
                    "AutoTask Ticket Status : %s%s\nAutoTask Ticket Priority : %s%s\nAutoTask Ticket QueueID : %s%s\nAutoTask Ticket Account ID : %s%s" %
                    (self.status, autotask_fields.get_field_label(autotask_fields.status_field, self.status),
                     self.priority, autotask_fields.get_field_label(autotask_fields.priority_field, self.priority),
                     self.queue_id, autotask_fields.get_field_label(autotask_fields.queue_id_field, self.queue_id),
                     self.account_id, autotask_fields.get_field_label(autotask_fields.account_id_field, self.account_id)))
            else:
                print("AutoTask Ticket Status : %s\nAutoTask Ticket Priority : %s\nAutoTask Ticket QueueID : %s\n\
AutoTask Ticket Account ID : %s" %
                      (self.status,
                       self.priority,
                       self.queue_id,
                       self.account_id))
        else:
            logger.info(
                "AutoTask Information: Ticket Status : %s, Ticket Priority : %s, Ticket QueueID : %s, Ticket Account ID : %s" %
                (self.status,
                 self.priority,
                 self.queue_id,
                 self.account_id))


class ConnectWiseInfo(ExtraInfo):
    def __init__(self):
        super(ConnectWiseInfo, self).__init__()
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.board_id = -1
        self.board_name = ""
        self.company_id = ""

    def get_info(self):
        return ("<cw_company_id:%s><cw_board_id:%s><cw_board_name:%s>" %
                (self.company_id, self.board_id, self.board_name))

    def parse_extra_info(self, extra_info):
        matches = re.match("<cw_company_id:(.*)><cw_board_id:(\d+)><cw_board_name:(.*)>", extra_info, re.IGNORECASE)
        if matches:
            self.company_id = matches.group(1)
            self.board_id = matches.group(2)
            self.board_name = matches.group(3)

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen is True:
            if (autotask_fields is not None):
                print("ConnectWise Company Id: %s \nConnectWise Board Id: %s (%s)" %
                      (self.company_id,
                       self.board_id, get_label(autotask_fields.board_ids, 0, self.board_id, True))
                      )
            else:
                print("ConnectWise Company Id: %s \nConnectWise Board Id : %s" %
                      (self.company_id, self.board_id))
        else:
            logger.info("ConnectWise Information: ConnectWise Company Id : %s, ConnectWise Board Id : %s" %
                        (self.company_id, self.board_id))


class FreshServiceInfo(ExtraInfo):
    def __init__(self):
        super(FreshServiceInfo, self).__init__()
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.status = -1
        self.priority = -1
        self.requester_id = -1
        self.requester_email = ""

    def get_info(self):
        return (
            "<freshservice_requester_id:%s><freshservice_requester_email:%s><freshservice_status:%s><freshservice_priority:%s>" %
            (self.requester_id, self.requester_email, self.status, self.priority))

    def parse_extra_info(self, extra_info):
        matches = re.match(
            "<freshservice_requester_id:(\d+)><freshservice_requester_email:(.*)><freshservice_status:(\d+)><freshservice_priority:(\d+)>",
            extra_info, re.IGNORECASE)
        if matches:
            self.requester_id = matches.group(1)
            self.requester_email = matches.group(2)
            self.status = matches.group(3)
            self.priority = matches.group(4)

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen is True:
            if autotask_fields is not None:
                print(
                    "FreshService Requester: %s (%s) \nFreshService Status: %s (%s) \nFreshService Priority: %s (%s)" %
                    (self.requester_id, get_label(autotask_fields.requesters, 0, self.requester_id, True),
                     self.status, get_label(autotask_fields.statuses, 0, self.status, True),
                     self.priority, get_label(autotask_fields.priorities, 0, self.priority, True))
                    )
            else:
                print("FreshService Requester: %s \nFreshService Status : %s \nFreshService Priority : %s" %
                      (self.requester_email, self.status, self.priority))
        else:
            logger.info(
                "FreshService Information: FreshService Requester : %s, FreshService Status : %s \nFreshService Priority : %s" %
                (self.requester_email, self.status, self.priority))


class SalesForceInfo(ExtraInfo):
    def __init__(self):
        super(SalesForceInfo, self).__init__()
        logger.info("Creating %s instance." % (self.__class__.__name__))
        self.security_token = ""
        self.account_id = ""
        self.contact_id = ""
        self.status = ""
        self.priority = ""

    def get_info(self):
        return (
        "<salesforce_security_token:%s><salesforce_account_id:%s><salesforce_contact_id:%s><salesforce_status:%s><salesforce_priority:%s>" %
        (self.security_token, self.account_id, self.contact_id, self.status, self.priority))

    def parse_extra_info(self, extra_info):
        matches = re.match(
            "<salesforce_security_token:(.*)><salesforce_account_id:(.*)><salesforce_contact_id:(.*)><salesforce_status:(.*)><salesforce_priority:(.*)>",
            extra_info, re.IGNORECASE)
        if matches:
            self.security_token = matches.group(1)
            self.account_id = matches.group(2)
            self.contact_id = matches.group(3)
            self.status = matches.group(4)
            self.priority = matches.group(5)

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen is True:
            if autotask_fields is not None:
                print(
                    "SalesForce Account: %s (%s) \nSalesForce Contact: %s (%s) \n"
                    "SalesForce Status: %s (%s) \nSalesForce Priority: %s (%s)" %
                    (self.account_id, get_label(autotask_fields.accounts, 0, self.account_id, True),
                     self.contact_id, get_label(autotask_fields.contacts, 0, self.contact_id, True),
                     get_label(autotask_fields.statuses, 1, self.status), self.status,
                     get_label(autotask_fields.priorities, 1, self.priority), self.priority)
                    )
            else:
                print("SalesForce Account: %s \nSalesForce Contact: %s \n"
                      "SalesForce Status : %s \nSalesForce Priority : %s" %
                      (self.account_id, self.contact_id, self.status, self.priority))
        else:
            logger.info("SalesForce Information: SalesForce Account Id : %s, "
                        "SalesForce Contact Id : %s, SalesForce Status : %s, SalesForce Priority : %s" %
                        (self.account_id, self.contact_id, self.status, self.priority))


class ServiceNowInfo(ExtraInfo):
    def __init__(self):
        super(ServiceNowInfo, self).__init__()
        logger.info("Creating %s instance." % self.__class__.__name__)
        self.caller_id = ""
        self.impact = ""
        self.urgency = ""

    def get_info(self):
        return "<servicenow_impact:%s><servicenow_urgency:%s><servicenow_caller_id:%s>" % (self.impact, self.urgency,
                                                                                             self.caller_id)

    def parse_extra_info(self, extra_info):
        matches = re.match("<servicenow_impact:(\d+)><servicenow_urgency:(\d+)><servicenow_caller_id:(.*)>",
                           extra_info, re.IGNORECASE)
        if matches:
            self.impact = matches.group(1)
            self.urgency = matches.group(2)
            self.caller_id = matches.group(3)

    def print_info(self, on_screen=False, autotask_fields=None):
        if on_screen is True:
            if autotask_fields is not None:
                print("ServiceNow Impact: %s(%s) \nServiceNow Urgency: %s(%s) \nServiceNow Caller: %s (%s)" % (
                    self.impact, get_label(autotask_fields.impact_val, 0, self.impact, True),
                    self.urgency, get_label(autotask_fields.urgency_val, 0, self.urgency, True),
                    self.caller_id, get_label(autotask_fields.caller_ids, 0, self.caller_id, True)))
            else:
                print("ServiceNow Impact: %s \nServiceNow Urgency: %s  \n"
                      "ServiceNow Caller Id: %s" % (self.impact, self.urgency, self.caller_id))
        else:
            logger.info("ServiceNow Information:: ServiceNow Impact: %s, ServiceNow Urgency: %s, "
                        "ServiceNow Caller_id: %s" % (self.impact, self.urgency, self.caller_id))