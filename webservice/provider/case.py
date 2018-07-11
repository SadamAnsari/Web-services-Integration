#!/usr/bin/python
import customer.customer as customer
import logging
import xml.etree.cElementTree as ElementTree
from datetime import date, datetime, time, timedelta

logger = logging.getLogger("Notification")


class Case:
    def __init__(self, case_response):
        if not case_response:
            raise Exception ("Failed to Initialize Case as case_response is not set.")
        logger.info("Creating %s instance for case :%s"
                    % (self.__class__.__name__, case_response.caseID))
        self.case_id = case_response.caseID
        self.customer_id = case_response.customerId
        self.customer_name = case_response.customerName
        self.name = case_response.name
        self.description = case_response.description
        self.external_ticket = case_response.externalTicket
        self.status = case_response.status
        self.events = self.parse_case_events(case_response.events)
        self.message = self.parse_case_message(case_response.events)
        self.procedures = self.parse_case_procedures(case_response.procedures)

        self.case_print()

    def parse_case_message(self, events):
        if events and len(events) > 0:
            for event in events:
                if event.deviceAlarmDescription and len (event.deviceAlarmDescription) > 0:
                    return event.deviceAlarmDescription
                if event.message and len (event.message) > 0:
                    return event.message

        raise Exception("Case %s neither have message nor deviceAlarmDescription in events list" % self.case_id)

    def parse_case_events(self, events):
        case_events = {}
        if events and len(events) > 0:
            for event in events:
                event_id = event.eventID
                if event_id and len(event_id) <= 0:
                    continue
                case_events[event_id] = event
        return case_events

    def parse_description(self, description_xml):
        description = ""
        try:
            root = ElementTree.fromstring(description_xml)
            remarks = []
            for remark in root.findall('./remarks'):
                if remark is not None and remark.text is not None and len(remark.text) > 0:
                    remarks.append(remark.text)
            description = "\n".join(remarks)
            steps = []
            for step in root.findall('./step'):
                id = "Step X"
                if step is not None and step.attrib is not None and len(step.attrib) > 0 and ("id" in step.attrib.keys()):
                    id = step.attrib["id"]
                step_data = step.find("data")
                # print step_data.text
                if step is not None:
                    if id is not None and step_data.text is not None and len(step_data.text) > 0:
                        steps.append("%s - %s" % (id, step_data.text))
                    elif step_data.text is None:
                        steps.append("%s" % id)

            description = "\n".join(remarks)
            if len(description) > 0:
                description = description + "\n\n"
            description = description + "\n".join(steps)
        except Exception, ex:
            logger.exception(ex)
        return description if len(description) > 0 else description_xml

    def get_ticket_description(self):

        ticket_description = ""
        if (self.procedures):
            counter = 1
            for procedure in self.procedures:
                procedure_type = " (%s) " % str(procedure.type) if procedure.type else ""
                ticket_description = "%s\nProcedure %d - %s%s\n%s\n" % (
                                             ticket_description,
                                             counter, str(procedure.name), procedure_type,
                                             self.parse_description(procedure.description))
                counter = counter + 1

        return ticket_description
    def parse_case_procedures(self, procedures):
        #ToDo: Process description in case required.
        return procedures
    def map_to_autotask(self):
        raise Exception("Method map_to_connectwise not implemented")

    def map_to_connectwise(self):
        raise Exception("Method map_to_connectwise not implemented")

    def map_to_ticketing_system(self, ticketing_api):
        if ticketing_api == customer.TICKETING_API_AUTOTASK:
            return self.map_to_autotask()
        elif ticketing_api == customer.TICKETING_API_CONNECTWISE:
            return self.map_to_connectwise()
        raise Exception ("Ticketing API type: %s, is not supported" % ticketing_api)

    def get_due_date(self, delta = 72):
        delta = delta if delta > 0 else 0
        return datetime.combine(date.today(), datetime.now().time()) + timedelta(hours=delta)

    def get_ticket_title(self, max_length):
        return self.name[:max_length]

    def case_print(self):
        logger.info("Case Instance:: ID : %s, Name : '%s', Cust ID: : '%s', Cust Name: : '%s', External Ticket: : '%s', Title: : '%s'"
                    % (self.case_id, self.name,
                       self.customer_id, self.customer_name,
                       self.external_ticket, self.message))