#!/usr/bin/python
# soapclient.py - SOAP client class, part of BlackStratus.

"""
    Provider level access to SOAP service.
"""
from suds import WebFault
import webservice.soapclient
import logging
# import xml.etree.ElementTree as ElementTree
import xml.etree.cElementTree as ElementTree

logger = logging.getLogger("Notification")
AUTOTASK_SUCCESS = 1


class Autotask(webservice.soapclient.TrSoapClient):
    # def __init__(self, wsdl_url = , username, password):
    def __init__(self, wsdl_url="", username="", password=""):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__,
                                                                   wsdl_url, username))
        webservice.soapclient.TrSoapClient.__init__(self, wsdl_url, username,
                                                    password)
        self.options.cache.clear()
        self.account_id = -1
        self.ticket_priority = -1  # High
        self.ticket_queue_id = -1  # Autotask Specific
        self.ticket_status = -1  # new
        """
        NOTE: With the current redesign of Autotask's workflow engine, API queries for TicketNote entities with 
        Publish = 1 now include all System Workflow Notes. If your query currently includes code that specifies 
        TickektNote.Publish = 1 and you do not want system workflow notes returned, you must modify the query to 
        include a condition that excludes TicketNote.NoteType = 13.
        """
        self.ticket_note_type = 1
        self.ticket_note_publish = 1
        self.SYSTEM_NOTE_TYPE = 13

        self.ticket_number = ""

    def set_mandatory_fields(self, autotask_info):
        self.account_id = autotask_info.account_id
        self.ticket_priority = autotask_info.priority
        self.ticket_queue_id = autotask_info.queue_id
        self.ticket_status = autotask_info.status

        logger.info("Setting autotask mandatory fileds.")
        autotask_info.print_info()

    def test(self):

        #         ati = self.factory.create('AutotaskIntegrations');
        #         fieldInfo = self.service.GetFieldInfo("Ticket")
        #         print fieldInfo
        #         return

        ticket = self.factory.create('Ticket')
        # print ticket
        ticket.id = 0
        ticket.AccountID = 0
        ticket.DueDateTime = case.get_due_date()
        ticket.Priority = 4
        ticket.QueueID = 5
        ticket.Status = 1
        ticket.Title = "Adding through Python"
        ticket.TicketType = 2

        #         ticket_note = self.factory.create('TicketNote')
        #         ticket_note.id = 0
        #         ticket_note.Title = "Python Note"
        #         ticket_note.Description = "python Desc"
        #         ticket_note.NoteType = 13
        #         ticket_note.Publish = 1
        #         ticket_note.TicketID = 7860
        e_arr = self.factory.create("ArrayOfEntity")
        ATWSError = self.factory.create("ATWSError")

        # print ticket_note
        # return
        # print e_arr
        e_arr.Entity = [ticket]

        # print self.service.create(ticketArray)
        atws_response = self.service.create(e_arr)
        for ATWSError in atws_response.Errors:
            print ATWSError[1]
            print ATWSError[0].Message
        return
        queryString = """
        <queryxml version="1.0">
            <entity>TicketNote</entity>
            <query>
                <condition>
                    <field>TicketID<expression op="equals">7859</expression></field>
                </condition>
                <condition>
                    <field>NoteType<expression op="notequal">13</expression></field>
                </condition>
            </query>
        </queryxml>"""

        print queryString
        try:

            autotask_response = self.service.query(queryString)
            print autotask_response
        except WebFault, ex:
            print ex

    def get_entity_array(self, entity):
        entity_array = self.factory.create("ArrayOfEntity")
        entity_array.Entity = entity if isinstance(entity, list) else [entity]

        return entity_array

    def get_account_id(self, customer_name=None):
        # TODO : Based on final discussion it may be required to get account ID from customer Name
        return self.account_id

    def get_ticket_priority(self, customer_name=None):
        # TODO : Based on final discussion it may be required to get Priority from customer Name
        return self.ticket_priority

    def get_ticket_queue_id(self, customer_name=None):
        # TODO : Based on final discussion it may be required to get queue ID from customer Name
        return self.ticket_queue_id

    def get_ticket_status(self, customer_name=None):
        # TODO : Based on final discussion it may be required to get Status from customer Name
        return self.ticket_status

    def get_ticket_note_publish(self, customer_name=None):
        # TODO : Based on final discussion it may be required to get Note publish Status from customer Name
        return self.ticket_note_publish

    def get_ticket_note_type(self, customer_name=None):
        # TODO : Based on final discussion it may be required to get note type from customer Name
        return self.ticket_note_type

    def get_condition(self, field, operation, value):
        condition_string = """<condition>
                                    <field>%s<expression op="%s">%s</expression></field>
                                </condition>""" % (field, operation, value)
        return condition_string

    def prepare_query(self, enity, field, value, operation="equals"):
        field = field if isinstance(field, list) else [field]
        value = value if isinstance(value, list) else [value]
        operation = operation if isinstance(operation, list) else [operation]

        if (len(field) != len(value)) or (len(operation) != len(value)):
            raise Exception("Length Mis-match!!!field:%d, value:%d, operation:%d"
                            % (len(field), len(value), len(operation)))
        conditions = []
        for index in range(0, len(field)):
            conditions.append(self.get_condition(field[index], operation[index], value[index]))
        query_string = """
                        <queryxml version="1.0">
                            <entity>%s</entity>
                            <query>
                                %s
                            </query>
                        </queryxml>""" % (enity, "\n".join(conditions))
        return query_string

    def get_ticket_id_by_number(self, ticket_number):
        if (ticket_number == None or len(ticket_number) <= 0):
            raise Exception("Ticket Number passed to function get_ticket_id_by_number is empty.")
        query_string = self.prepare_query("Ticket", "TicketNumber", ticket_number)
        autotask_response = self.service.query(query_string)
        if autotask_response.ReturnCode == AUTOTASK_SUCCESS:
            ticket_id = autotask_response.EntityResults.Entity[0].id
            logger.info("Ticket id is %d for ticket number %s" %
                        (ticket_id, ticket_number))
            return ticket_id

        else:
            raise Exception("Failed to get Ticlet id for ticket number %s" % ticket_number)

    def get_existing_ticket_note_list(self, ticket_id):
        ticket_note_list = []
        query_string = self.prepare_query("TicketNote",
                                          ["TicketID", "NoteType"],
                                          [ticket_id, self.SYSTEM_NOTE_TYPE],
                                          ["equals", "notequal"]
                                          )
        autotask_response = self.service.query(query_string)
        if autotask_response.ReturnCode == AUTOTASK_SUCCESS:
            if (len(autotask_response.EntityResults) > 0 and
                        autotask_response.EntityResults.Entity is not None):
                for entity in autotask_response.EntityResults.Entity:
                    ticket_note_list.append(entity.Title.lower())
        else:
            error = str(autotask_response.Errors)
            raise Exception("Failed to get Ticket Notes for Ticket Id: %s. Error: %s (%s)" %
                            (ticket_id, error, autotask_response.ReturnCode))
        return ticket_note_list

    def add_ticket_notes(self, ticket_number, case):
        logger.info("Adding / Updating Ticket Notes in ticket %s for case : %s(%s)"
                    % (ticket_number, case.name, case.case_id))
        ticket_id = self.get_ticket_id_by_number(ticket_number)

        # get list of Existing tickets
        ticket_note_list = self.get_existing_ticket_note_list(ticket_id)
        logger.info("There are currently '%d' Ticket Notes in ticket number: %s (%s)"
                    % (len(ticket_note_list), ticket_number, ticket_id))
        ticket_notes = []
        for event_id, event in case.events.iteritems():
            if str(event_id).lower() not in ticket_note_list:
                ticket_note = self.factory.create('TicketNote')
                ticket_note.id = 0
                ticket_note.Title = str(event_id)
                ticket_note.Description = str(event)
                ticket_note.NoteType = self.get_ticket_note_type()
                ticket_note.Publish = self.get_ticket_note_publish()
                ticket_note.TicketID = ticket_id
                ticket_notes.append(ticket_note)
                self.print_ticket_note(ticket_note)
        if len(ticket_notes) > 0:
            ticket_notes_entity_array = self.get_entity_array(ticket_notes)
            logger.info("Adding %d Ticket Notes in ticket %s for case : %s(%s)"
                        % (len(ticket_notes), ticket_number, case.name, case.case_id))
            autotask_response = self.service.create(ticket_notes_entity_array)
        else:
            logger.error("No new event found for case : %s(%s)"
                         % (case.name, case.case_id))

    def print_ticket_note(self, ticket_note):
        logger.info("Ticket Note Instance:: Title : '%s', Note Type : '%s', Publish : '%s', TicketID : '%s'"
                    % (ticket_note.Title, ticket_note.NoteType,
                       ticket_note.Publish, ticket_note.TicketID))

    def print_ticket(self, ticket):
        logger.info(
            "Ticket Instance:: Title : '%s', Account ID : '%s', DueDate : '%s', Priority : '%s', Status : '%s', Queue ID : '%s'"
            % (ticket.Title, ticket.AccountID,
               ticket.DueDateTime, ticket.Priority,
               ticket.Status, ticket.QueueID))

    def add_ticket(self, case):
        ticket = self.factory.create('Ticket')
        ticket.id = 0
        ticket.AccountID = self.get_account_id()
        ticket.DueDateTime = case.get_due_date()
        ticket.Priority = self.get_ticket_priority()
        ticket.Status = self.get_ticket_status()
        ticket.Title = case.get_ticket_title(max_length=250)
        ticket.QueueID = self.get_ticket_queue_id()
        ticket_description = case.get_ticket_description()
        if ticket_description and len(ticket_description) > 0:
            ticket.Description = ticket_description

        self.print_ticket(ticket)

        ticket_entity_array = self.get_entity_array(ticket)
        autotask_response = self.service.create(ticket_entity_array)
        if autotask_response.ReturnCode == AUTOTASK_SUCCESS:
            ticket_id = autotask_response.EntityResults.Entity[0].id
            ticket_number = autotask_response.EntityResults.Entity[0].TicketNumber
            logger.info("Ticket Number %s created successfully for case : %s(%s). AutoTask Internal ID is %s" %
                        (ticket_number, case.name, case.case_id, ticket_id))
            return ticket_number
        else:
            error = str(autotask_response.Errors)
            raise Exception("Failed to created Ticket for Case %s(%s). Error: %s (%s)" %
                            (case.name, case.case_id, error, autotask_response.ReturnCode))

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

    def get_account_list(self, account_list, search_word):
        query_string = self.prepare_query("Account",
                                          ["AccountName", "Active"],
                                          [search_word, "1"],
                                          ["like", "equals"]
                                          )
        autotask_response = self.service.query(query_string)
        if autotask_response.ReturnCode == AUTOTASK_SUCCESS:
            if autotask_response.EntityResults:
                accounts = autotask_response.EntityResults.Entity
                if accounts and len(accounts) > 0:
                    for account in accounts:
                        account_list[account.id] = account.AccountName
            else:
                print "No records found. Search Again..."
