#!/usr/bin/python
import re
import requests
import webservice.restclient
from requests.auth import HTTPBasicAuth
from utility import add_http
import logging

logger = logging.getLogger("Notification")


class FreshService(webservice.restclient.TrRestClient):
    def __init__(self, server_url, username, password):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   server_url, username))
        webservice.restclient.TrRestClient.__init__(self, server_url, username,
                                                    password)
        self.requester_email = ""
        self.ticket_number = ""
        self.requester_id = -1
        self.status = -1
        self.priority = -1
        self.API_URL = add_http(server_url, is_secure=True)

    def get_add_ticket_url(self):
        return "%s/helpdesk/tickets.json" % self.API_URL

    def get_add_ticket_note_url(self, ticket_id, is_existing_note=False):
        if is_existing_note:
            return "%s/helpdesk/tickets/%s.json" % (self.API_URL, ticket_id)
        else:
            return "%s/helpdesk/tickets/%s/conversations/note.json" % (self.API_URL, ticket_id)

    def set_mandatory_fields(self, extra_info):
        self.requester_id = extra_info.requester_id
        self.requester_email = extra_info.requester_email
        self.status = extra_info.status
        self.priority = extra_info.priority

    def get_auth_token(self):
        return HTTPBasicAuth(self.username, self.password)

    def add_ticket_notes(self, ticket_id, case):
        auth_token = self.get_auth_token()
        url = self.get_add_ticket_note_url(ticket_id)
        logger.info("FreshService: Adding / Updating Ticket Notes in ticket %s for case : %s(%s)"
                    % (ticket_id, case.name, case.case_id))
        ticket_note_list = self.get_existing_ticket_note_list(ticket_id)
        logger.info("There are currently '%d' Ticket Notes in ticket number: %s"
                    % (len(ticket_note_list), ticket_id))
        ticket_notes = []
        for event_id, event in case.events.iteritems():
            if str(event_id).upper() not in ticket_note_list:
                logger.info("Event Id: %s is new in ticket %s." %
                            (str(event_id).upper(), ticket_id))
                ticket_notes.append(str(event))
        if len(ticket_notes) > 0:
            logger.info("Adding %d Ticket Notes in ticket %s for case : %s(%s)"
                        % (len(ticket_notes), ticket_id, case.name, case.case_id))
            for item in range(len(ticket_notes)):
                notes = {
                    "helpdesk_note": {
                        "body": ticket_notes[item],
                        "private": False
                    }
                }
                response = requests.post(url, auth=auth_token, json=notes)
                if response.status_code != 200:
                    logger.error("Failed to post data. Error Code: %s" % response.status_code)
                    raise Exception("Exception caught: Method:Post, Response Code: %s, URL: %s" %
                                    (response.status_code, url))
        else:
            logger.error("No new event found for case : %s(%s)"
                         % (case.name, case.case_id))

    def get_existing_ticket_note_list(self, ticket_id):
        ticket_note_list = []
        auth_token = self.get_auth_token()
        url = self.get_add_ticket_note_url(ticket_id, is_existing_note=True)
        response = requests.get(url, auth=auth_token)
        logger.info("Method:GET, Response Code: %s, URL: %s" %
                    (response.status_code, url))
        if response.status_code != 200:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        else:
            data = response.json()
            if data and len(data['helpdesk_ticket']['notes']) >= 0:
                for notes in data['helpdesk_ticket']['notes']:
                    if 'body' not in notes['note'].keys():
                        continue
                    matchobj = re.findall("eventID\s*=\s*(\S+)", notes['note']['body'], re.MULTILINE)
                    if matchobj:
                        ticket_note_list.append(matchobj[0].strip('"').upper())
                return ticket_note_list

    def add_ticket(self, case):
        logger.info("Adding FreshService ticket for case: %s" % case.case_id)
        auth_token = self.get_auth_token()
        url = self.get_add_ticket_url()
        data = {
            "helpdesk_ticket": {
                "description": case.get_ticket_description(),
                "subject": case.get_ticket_title(max_length=250),
                "email": self.requester_email,
                "status": self.status,
                "priority": self.priority,
                "source": 2,
                "ticket_type": "Incident"
            }
        }
        response = requests.post(url, auth=auth_token, json=data)
        logger.info("Method:Post, Response Code: %s, URL: %s" %
                    (response.status_code, url))
        if response.status_code != 200:
            logger.error("Failed to post data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:POST, Response Code: %s, URL: %s" %
                            (response.status_code, url))
        else:
            data = response.json()
            self.print_ticket(data)
            ticket_number = data['item']['helpdesk_ticket']['display_id']
            logger.info("Ticket Number %s created successfully for case : %s(%s)." %
                        (ticket_number, case.name, case.case_id))
            return str(ticket_number)

    def print_ticket(self, data):
        logger.info("Ticket Instance:: Title : '%s','Due Date': '%s', Priority : '%s', Status : '%s'"
                    % (data['item']['helpdesk_ticket']['subject'],
                       data['item']['helpdesk_ticket']['due_by'],
                       data['item']['helpdesk_ticket']['priority'],
                       data['item']['helpdesk_ticket']['status']))

    def save(self, case):
        if case.external_ticket and len(case.external_ticket) > 0:
            logger.info("FreshService: Updating Existing Ticket: %s for case : %s(%s)"
                        % (case.external_ticket, case.name, case.case_id))
            self.add_ticket_notes(case.external_ticket, case)
            self.ticket_number = case.external_ticket
        else:
            logger.info("FreshService: Creating New Ticket for case : %s(%s)"
                        % (case.name, case.case_id))
            self.ticket_number = self.add_ticket(case)
            self.add_ticket_notes(self.ticket_number, case)