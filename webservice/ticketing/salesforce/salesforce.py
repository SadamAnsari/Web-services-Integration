#!/usr/bin/python

import beatbox
import logging
from customer import *

logger = logging.getLogger("Notification")


class SalesForce:
    def __init__(self, wsdl_url="", username="", password=""):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   wsdl_url, username))
        self.username = username
        self.password = password
        self.security_token = ""
        self.status = ""
        self.priority = ""
        self.contact_id = ""
        self.account_id = ""
        self.ticket_number = ""
        self.service = beatbox.PythonClient()

    def set_mandatory_fields(self, salesforce_info):
        self.security_token = salesforce_info.security_token
        self.contact_id = salesforce_info.contact_id
        self.account_id = salesforce_info.account_id
        self.status = salesforce_info.status
        self.priority = salesforce_info.priority

        self.service.login(self.username, self.password + self.security_token)

    def add_ticket(self, case):
        logger.info("Adding SalesForce ticket for case: %s" % case.case_id)
        ticket_dict = {
            'type': 'Case',
            'AccountId': self.account_id,
            'ContactId': self.contact_id,
            'Status': self.status,
            'Priority': self.priority,
            'Subject': case.get_ticket_title(max_length=255),
            'Description': case.get_ticket_description()
        }
        response = self.service.create(ticket_dict)
        if response[0]['success']:
            ticket_id = response[0]['id']
            ticket_number = self.get_case_number_from_id(ticket_id)
            # print "inside add_ticket_function: Ticket Number: %s" % str(ticket_number)
            self.print_data(str(ticket_number))
            logger.info("Ticket Number %s created successfully for case : %s(%s)." %
                        (str(ticket_number), case.name, case.case_id))
            return str(ticket_number)
        else:
            raise Exception("Error creating ticket: %s" % (", ".join(response[0]['errors'])))

    def add_ticket_notes(self, ticket_number, case):
        # print "inside add_ticket_notes: ticket_number: %s"% ticket_number
        ticket_number = str(ticket_number)
        ticket_id = self.get_id_from_ticket_number(ticket_number)
        logger.info("SalesForce: Adding / Updating Ticket Notes in ticket %s for case : %s(%s)"
                    % (ticket_number, case.name, case.case_id))
        ticket_note_list = self.get_existing_ticket_note_list(ticket_number)
        logger.info("There are currently '%d' Ticket Notes in ticket number: %s"
                    % (len(ticket_note_list), ticket_number))
        ticket_notes = []
        for event_id, event in case.events.iteritems():
            if str(event_id).upper() not in ticket_note_list:
                logger.info("Event Id: %s is new in ticket %s." %
                            (str(event_id).upper(), ticket_number))
                ticket_notes.append(str(event))
        if len(ticket_notes) > 0:
            logger.info("Adding %d Ticket Notes in ticket %s for case : %s(%s)"
                        % (len(ticket_notes), ticket_number, case.name, case.case_id))
            for comment in range(len(ticket_notes)):
                comment_dict = {
                    "type": "CaseComment",
                    "CommentBody": ticket_notes[comment],
                    "ParentId": ticket_id
                }
                self.service.create(comment_dict)
            logger.info("Ticket Notes updated for Ticket Number: %s" % (ticket_number))
        else:
            logger.error("No new event found for case : %s(%s)" % (case.name, case.case_id))

    def get_existing_ticket_note_list(self, ticket_number):
        # print "inside get_existing_ticket_note_list: %s"%ticket_number
        ticket_id = self.get_id_from_ticket_number(ticket_number)
        results = self.service.query("SELECT CommentBody from CaseComment WHERE ParentId='%s'" % ticket_id)
        ticket_note_list = []
        if len(results) > 0:
            for comments in range(len(results)):
                matchobj = re.findall("eventID\s*=\s*(\S+)", results[comments]['CommentBody'], re.MULTILINE)
                if matchobj:
                    ticket_note_list.append(matchobj[0].strip('"').upper())
        return ticket_note_list

    def get_case_number_from_id(self, ticket_id):
        result_set = self.service.query("SELECT CaseNumber FROM Case WHERE Id='%s'" % ticket_id)
        if len(result_set) > 0:
            ticket_number = result_set[0]['CaseNumber']
            return str(ticket_number)
        else:
            raise Exception("No records found for given ticket_id: %s" % ticket_id)

    def get_id_from_ticket_number(self, ticket_number):
        result_set = self.service.query("SELECT Id FROM Case WHERE CaseNumber = '%s'" % ticket_number)
        if len(result_set) > 0:
            ticket_id = result_set[0]['Id']
            return ticket_id
        else:
            raise Exception("No records found for given ticket_number: %s" % ticket_number)

    def save(self, case):
        if case.external_ticket and len(case.external_ticket) > 0:
            logger.info("Updating Existing Ticket: %s for case : %s(%s)"
                        % (case.external_ticket, case.name, case.case_id))
            self.add_ticket_notes(case.external_ticket, case)
            self.ticket_number = case.external_ticket
        else:
            logger.info("Creating New Ticket for case : %s(%s)"
                        % (case.name, case.case_id))
            self.ticket_number = self.add_ticket(case)
            self.add_ticket_notes(self.ticket_number, case)

    def print_data(self, ticket_number):
        result_set = self.service.query("SELECT Id, Subject, Status, Priority from Case WHERE CaseNumber='%s'"
                                        % ticket_number)
        logger.info("Ticket Instance:: Title : '%s' , Status : '%s', Priority : '%s'"
                    % (result_set[0]['Subject'],
                       result_set[0]['Status'],
                       result_set[0]['Priority'])
                    )
