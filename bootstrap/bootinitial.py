#!/usr/bin/python
import sys
from customer.customer import *
from customer.extrainfo import get_label
from webservice.ticketing.autotask import AutoTaskFields, Autotask
from webservice.ticketing.jira import Jira
from webservice.ticketing.connectwise import ConnectWiseFields
from webservice.ticketing.freshservice import FreshServiceFields
from webservice.ticketing.salesforce import SalesForceFields
from webservice.ticketing.servicenow import ServiceNowFields


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = "y/n"
    elif default == "yes":
        prompt = "Y/n"
    elif default == "no":
        prompt = "y/N"
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = get_user_input(question + "(yes|no)")
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]


def get_user_input(message, default_val=""):
    if len(default_val) > 0:
        message = "%s [%s]" % (message, default_val)
    message = "\n%s:" % message
    user_input = ""
    try:
        user_input = raw_input(message)
    except NameError:
        user_input = input(message)
    user_input = user_input.strip()
    if len(default_val) > 0 and len(user_input) <= 0:
        user_input = default_val
    return user_input


def get_autotask_account_name_input(message):
    value = get_user_input(message, 'All').strip()
    if value.lower() == 'all':
        value = '%'
    else:
        value = value.replace('"', '').replace("'", '')
        value = str(value) + "%"
    return value


def get_servicenow_callers(message):
    value = get_user_input(message, 'All').strip()
    if value.lower() == 'all':
        value = ''
    else:
        value = value.replace('"', '').replace("'", '')
    return value


def get_Jira_input(field, projects, selected_index=None):
    field_val = -1
    counter = 1
    if selected_index is None:
        for project in projects:
            key = project['id']
            value = project['name']
            field_val = 1
            print "%d : %s (%s)" % (counter, value, key)
            counter += 1
    else:
        for item in projects[selected_index - 1]['issuetype']:
            field_val = 1
            print "%d : %s" % (counter, item)
            counter += 1

    if field_val < 0:
        raise Exception("No data present for %s field." % field)
    while True:
        selected_val = int(get_user_input("Select default %s" % field, str(field_val)))
        if selected_val > 0 and selected_val < counter:
            break
        print ("Invalid input (%s) selected for %s field. Re-trying" %
               (selected_val, field))
    if selected_index is None:
        return selected_val, projects[selected_val - 1]['id']
    else:
        return projects[selected_index - 1]['issuetype'][selected_val - 1]


def get_bootstrap_input(field, values, index=None):
    # print values
    field_val = -1
    id_list = []
    if index is None:
        for key, value in values.iteritems():
            print "%s : %s" % (key, value)
            id_list.append(int(key))
        field_val = values.keys()[0]
    else:
        for key, value in values.iteritems():
            print "%s : %s" % (key, value[1])
            id_list.append(key)
        field_val = values.keys()[0]
    if field_val == -1:
        raise Exception("No data present for %s field." % field)
    while True:
        selected_val = int(get_user_input("Select default %s" % field, str(field_val)))
        if selected_val in id_list:
            break
        print ("Invalid input (%s) selected for %s field. Re-trying" %
               (selected_val, field))
    if index is None:
        return selected_val
    else:
        return values[selected_val][index]


def load_extra_fields(customer):
    autotask_fields = None
    if customer.ticket_api == TICKETING_API_AUTOTASK:
        try:
            print ("Connecting to AutoTask ticketing system")
            autotask_client = Autotask(customer.url, customer.username, customer.password)
            autotask_fields = AutoTaskFields(autotask_client)
        except Exception, ex:
            logger.exception(ex)
            return
        print ("Loading AutoTask mandatory field details")
        extra_fields = autotask_fields.load_fields()
        if extra_fields:
            customer.extra_info.status = get_bootstrap_input(autotask_fields.status_field, extra_fields[0], 0)
            customer.extra_info.priority = get_bootstrap_input(autotask_fields.priority_field, extra_fields[1], 0)
            customer.extra_info.queue_id = get_bootstrap_input(autotask_fields.queue_id_field, extra_fields[2], 0)
            while True:
                search_account_name = get_autotask_account_name_input(
                    "Search Account Name starts with (Hit enter to search All)")
                account_fields = autotask_fields.load_account_fields(search_account_name)
                if len(account_fields) > 0:
                    customer.extra_info.account_id = get_bootstrap_input(autotask_fields.account_id_field,
                                                                         extra_fields[3], 0)
                    break
        return autotask_fields
    elif customer.ticket_api == TICKETING_API_JIRA:
        print ("Connecting to Jira ticketing system")
        jira_client = Jira(customer.url, customer.username, customer.password)
        extra_fields = jira_client.load_fields()
        if extra_fields:
            selected_index, customer.extra_info.account_id = get_Jira_input("Account/Project", extra_fields)
            customer.extra_info.issuetype = get_Jira_input("Account/Project", extra_fields, selected_index)
    elif customer.ticket_api == TICKETING_API_CONNECTWISE:
        customer.extra_info.company_id = get_user_input("Enter Company ID", customer.extra_info.company_id)
        cw_fields = None
        try:
            print ("Connecting to ConnectWise ticketing system")
            #             cw_client = ConnectWise(customer.url, customer.username, customer.password)
            cw_fields = ConnectWiseFields(customer.url, customer.username, customer.password,
                                          customer.extra_info.company_id)
        except Exception, ex:
            logger.exception(ex)
            return
        print("Loading ConnecWise mandatory field details")
        extra_fields = cw_fields.load_boards_fields()
        if extra_fields:
            customer.extra_info.board_id = get_bootstrap_input("Board Id", extra_fields[0], 0)
            print extra_fields[0]
            customer.extra_info.board_name = get_label(extra_fields[0], 0, customer.extra_info.board_id, True)
            # status_fields = cw_fields.load_status_fields(customer.extra_info.board_id)
        return cw_fields
    elif customer.ticket_api == TICKETING_API_FRESHSERVICE:
        freshservice_fields = None
        try:
            print ("Connecting to FreshService ticketing system")
            freshservice_fields = FreshServiceFields(customer.url, customer.username, customer.password)
        except Exception, ex:
            logger.exception(ex)
            return
        print("Loading FreshService mandatory field details")
        extra_fields = freshservice_fields.load_fields()
        if extra_fields:
            customer.extra_info.requester_id = get_bootstrap_input("Requester Email", extra_fields[0], 0)
            customer.extra_info.requester_email = get_label(extra_fields[0], 0, customer.extra_info.requester_id, True)
            customer.extra_info.status = get_bootstrap_input("Status", extra_fields[1], 0)
            customer.extra_info.priority = get_bootstrap_input("Priority", extra_fields[2], 0)
        return freshservice_fields
    elif customer.ticket_api == TICKETING_API_SALESFORCE:
        customer.extra_info.security_token = get_user_input("Enter Security Token", customer.extra_info.security_token)
        salesforce_fields = None
        try:
            print ("Connecting to SalesForce ticketing system")
            salesforce_fields = SalesForceFields(customer.url, customer.username, customer.password,
                                                 customer.extra_info.security_token)
        except Exception, ex:
            logger.exception(ex)
            return
        print("Loading SalesForce mandatory field details")
        extra_fields = salesforce_fields.load_fields()
        if extra_fields:
            customer.extra_info.account_id = get_bootstrap_input("Account Id", extra_fields[0], 0)
            contact_list = salesforce_fields.get_contacts(customer.extra_info.account_id)
            customer.extra_info.contact_id = get_bootstrap_input("Contact Id", contact_list, 0)
            customer.extra_info.status = get_bootstrap_input("Status", extra_fields[1], 1)
            customer.extra_info.priority = get_bootstrap_input("Priority", extra_fields[2], 1)
        return salesforce_fields
    elif customer.ticket_api == TICKETING_API_SERVICENOW:
        servicenow_fields = None
        try:
            print ("Connecting to ServiceNow ticketing system")
            servicenow_fields = ServiceNowFields(customer.url, customer.username, customer.password)
        except Exception, ex:
            logger.exception(ex)
            return
        print("Loading ServiceNow mandatory field details")
        extra_fields = servicenow_fields.load_fields()
        if extra_fields:
            customer.extra_info.impact = get_bootstrap_input("Impact", extra_fields[0], 0)
            customer.extra_info.urgency = get_bootstrap_input("Urgency", extra_fields[1], 0)
            while True:
                search_caller_name = get_servicenow_callers(
                    "Search Caller Name starts with (Hit enter to search All)")
                caller_fields = servicenow_fields.get_caller_ids(search_caller_name)
                if len(caller_fields) > 0:
                    customer.extra_info.caller_id = get_bootstrap_input("Caller Id", extra_fields[2], 0)
                    break
        return servicenow_fields
