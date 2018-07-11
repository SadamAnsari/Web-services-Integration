#!/usr/bin/python

import re
import json
import webservice.restclient
from utility import add_http
import logging

logger = logging.getLogger("Notification")


class ServiceNow(webservice.restclient.TrRestClient):
    def __init__(self, server_url, username, password):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   server_url, username))
        webservice.restclient.TrRestClient.__init__(self, server_url, username,
                                                    password)
        self.caller = ""
        self.impact = ""
        self.urgency = ""
        self.ticket_number = ""
        self.API_URL = add_http(server_url, is_secure=True)

    def set_mandatory_fields(self, extra_info):
        self.impact = extra_info.impact
        self.urgency = extra_info.urgency
        self.caller = extra_info.caller_id

    def get_add_ticket_url(self):
        return "%s/api/now/v2/table/incident" % self.API_URL

    def get_add_ticket_note_url(self, sys_id):
        return "%s/api/now/v2/table/incident/%s" % (self.API_URL, sys_id)

    def get_existing_notes_url(self, sys_id):
        return "%s/api/now/v2/table/sys_journal_field?element_id=%s" % (self.API_URL, sys_id)

    def get_sys_id_url(self, ticket_number):
        return "%s?sysparm_query=active=true^number=%s" % (self.get_add_ticket_url(), ticket_number)

    def get_sys_id(self, ticket_number):
        url = self.get_sys_id_url(ticket_number)
        data = self.get(url)
        ticket_id = data['result'][0]['sys_id'] if len(data['result']) > 0 else ''
        return ticket_id

    def get_existing_ticket_note_list(self, ticket_id):
        ticket_note_list = []
        url = self.get_existing_notes_url(ticket_id)
        data = self.get(url)
        if data and len(data['result']) >= 0:
            for i in range(len(data['result'])):
                if 'value' not in data['result'][i].keys():
                    continue
                matchobj = re.findall("eventID\s*=\s*(\S+)", data['result'][i]['value'], re.MULTILINE)
                if matchobj:
                    ticket_note_list.append(matchobj[0].strip('"').upper())
        return ticket_note_list

    def add_ticket_notes(self, ticket_number, case):
        ticket_id = self.get_sys_id(ticket_number)
        # print "ticket_id: %s" % ticket_id
        url = self.get_add_ticket_note_url(ticket_id)
        logger.info("ServiceNow: Adding / Updating Ticket Notes in ticket %s for case : %s(%s)"
                    % (ticket_number, case.name, case.case_id))
        ticket_note_list = self.get_existing_ticket_note_list(ticket_id)
        logger.info("There are currently '%d' Ticket Notes in ticket number: %s"
                    % (len(ticket_note_list), ticket_number))
        ticket_notes = []
        # count = 0
        for event_id, event in case.events.iteritems():
            if str(event_id).upper() not in ticket_note_list:
                logger.info("Event Id: %s is new in ticket %s." %
                            (str(event_id).upper(), ticket_number))
                ticket_notes.append(str(event))
                # count += 1
                # if count == 2:
                #     break
        if len(ticket_notes) > 0:
            logger.info("Adding %d Ticket Notes in ticket %s for case : %s(%s)"
                        % (len(ticket_notes), ticket_number, case.name, case.case_id))
            for item in range(len(ticket_notes)):
                notes = '{"work_notes": %s}' % json.dumps(ticket_notes[item])
                data = self.put(url, notes, response_code=200)
            logger.info("Ticket Notes updated for Ticket Number: %s" % ticket_number)
        else:
            logger.error("No new event found for case : %s(%s)"
                         % (case.name, case.case_id))

    def add_ticket(self, case):
        logger.info("Adding ServiceNow ticket for case: %s" % case.case_id)
        url = self.get_add_ticket_url()
        post_data = "{'short_description': %s, 'comments': %s, 'caller_id': %s, 'impact':%s, 'urgency':%s}" % (
            json.dumps(case.get_ticket_title(max_length=250)),
            json.dumps(case.get_ticket_description()),
            json.dumps(self.caller), self.impact, self.urgency)
        data = self.post(url, post_data, response_code=201)
        self.print_ticket(data)
        ticket_number = data['result']['number']
        logger.info("Ticket Number %s created successfully for case : %s(%s)." %
                    (ticket_number, case.name, case.case_id))
        return str(ticket_number)

    def print_ticket(self, data):
        logger.info("Ticket Instance:: Title : '%s', Impact: '%s', Urgency: '%s', Priority: '%s'" % (
            data['result']['short_description'],
            data['result']['impact'],
            data['result']['urgency'],
            data['result']['priority']))

    def save(self, case):
        # case.external_ticket = ""
        if case.external_ticket and len(case.external_ticket) > 0:
            logger.info("ServiceNow: Updating Existing Ticket: %s for case : %s(%s)"
                        % (case.external_ticket, case.name, case.case_id))
            self.add_ticket_notes(case.external_ticket, case)
            self.ticket_number = case.external_ticket
        else:
            logger.info("ServiceNow: Creating New Ticket for case : %s(%s)"
                        % (case.name, case.case_id))
            self.ticket_number = self.add_ticket(case)
            self.add_ticket_notes(self.ticket_number, case)
