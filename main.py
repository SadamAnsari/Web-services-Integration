#!/usr/bin/python


import os, getopt
import sys
import logging
import traceback as tb

from webservice.provider import CaseClient
from webservice.ticketing.autotask import Autotask
from webservice.ticketing.jira import Jira
from webservice.ticketing.connectwise import ConnectWise
from webservice.ticketing.freshservice import FreshService
from webservice.ticketing.salesforce import SalesForce
from webservice.ticketing.servicenow import ServiceNow
from configuration import ProviderConfiguration
from logger import setup_logging
from webservice.provider import Case
from customer import *
from queue import Queue
from suds import WebFault


class Connector:
    def __init__(self, incident_id):
        self.incident_id = incident_id
        self.corelog = None
        self.queue = None
        self.provider_configuration = None
        self.customer_mapping = None
        self.ticketing_system = None
    
        self.stage = 0
        
    def add_case_to_queue(self, customer_id = 999999, customer_name = "SIM Provider", ticket_number=""):
        try:
            self.queue.add(customer_id, customer_name, ticket_number, self.stage)
        except IOError as e:
            self.corelog.error("add_case_to_queue I/O error(%d): %s" % (e.errno, e.strerror))
        except Exception, e:
            self.corelog.error("*** Failed to add case %d in queue." % (self.incident_id) )
            self.corelog.exception(e)
            
    def remove_case_from_queue(self):
        try:
            self.queue.remove(self.incident_id)
        except IOError as e:
            self.corelog.error("remove_case_from_queue I/O error(%d): %s" % (e.errno, e.strerror))
        except Exception, e:
            self.corelog.error("*** Failed to remove case %d from queue." % (self.incident_id) )
            self.corelog.exception(e)
         
    def initialize(self):
        """ Initialize file logger """
        try:
            setup_logging("Notification", os.path.join("data", "log"), scrnlog = False)
#             setup_logging("suds.client", os.path.join("data", "log"), scrnlog = True)
            self.corelog = logging.getLogger("Notification")
        except Exception, e:
            tb.print_exc()
            exit("Error Initializing logger")
        
        self.corelog.info("Starting notifier script for incident id: %s" % self.incident_id)
        self.queue = Queue(self.incident_id)
        
    def read_provider_configuration(self):
        try:
            self.corelog.debug("Reading Provider Configuration")
            self.provider_configuration = ProviderConfiguration()
            self.provider_configuration.read_configuration(os.path.dirname(os.path.realpath(__file__)))
            return
        except IOError as e:
            self.corelog.error("read_customer_mapping I/O error(%d): %s" % (e.errno, e.strerror))    
        except Exception, e:
            self.corelog.error("Exception caught in read_provider_configuration.")
            
            self.corelog.exception(e)
        self.add_case_to_queue()
        exit("Error Reading provider Configuration")
        
    def read_customer_mapping(self):
        try:
            mapping_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        self.provider_configuration.customer_mapping_path)
            self.corelog.debug("Reading Customer Mapping from %s" 
                               % mapping_file)
            self.customer_mapping = CustomerMapping(mapping_file)
            if self.customer_mapping.read_mapping() <= 0:
                raise Exception ("No Customer information found at %s" % 
                                 mapping_file)
            return
        except IOError as e:
            self.corelog.error("read_customer_mapping I/O error(%d): %s" % (e.errno, e.strerror))   
        except Exception, e:
            self.corelog.error("Exception caught in read_customer_mapping.")
            self.corelog.exception(e)
        self.add_case_to_queue()
        exit("Error Reading Customer Mapping File")
                        
    def get_case_details_from_provider(self):
        try:
            self.corelog.debug("Reading case (%s) details from provider"
                               % self.incident_id)
            caseclient = CaseClient(self.provider_configuration.url, self.provider_configuration.username, 
                                        self.provider_configuration.password)
        
            providercase = caseclient.get_case_detail(self.incident_id)
            if providercase and len(providercase) > 0:
                """ Valid Response """
                case = Case(providercase[0])
                return case
            self.corelog.error("Failed to get case details for case %d." % self.incident_id)   
        except WebFault, f:
            self.corelog.error("Failed to query case details for case %d. Fault: %s" % (self.incident_id, f.fault ))
        except Exception, e:
            self.corelog.error("Exception caught in get_case_details_from_provider.")
            self.corelog.exception(e)
            
        self.add_case_to_queue()   
        exit("Error Reading Case Details from provider")
    
    def get_customer_details(self, customer_id, customer_name):
        try:
            self.corelog.debug("Fetching customer's '%s(ID: %s)' details from mapping data"
                               % (customer_name, customer_id))
            customer = self.customer_mapping.get_customer(customer_id)
            if customer:
                customer.print_info()
                return customer
            self.corelog.error("Failed to get customer's '%s(ID: %s)' details from mapping data for case %s." % 
                          (customer_name, customer_id, self.incident_id))
        except WebFault, f:
            self.corelog.error("Failed to query case details for case %d. Fault: %s" % (self.incident_id, f.fault ))
        except Exception, e:
            self.corelog.error("Exception caught in get_case_details_from_provider.")
            self.corelog.exception(e)
            
        self.add_case_to_queue()   
        exit("Error Fetching customer details from mapping data")
        
    def update_ticketing_system(self, case_detail, customer_detail):
        try:
            ticket_number = ""
            self.corelog.debug("Updating (%s) Ticketing system for customer: %s, url: %s" 
                               % (TICKET_API[customer_detail.ticket_api],
                               case_detail.customer_name, customer_detail.url))
            if customer_detail.ticket_api == TICKETING_API_AUTOTASK:
                self.ticketing_system = Autotask(customer_detail.url, customer_detail.username, 
                                                          customer_detail.password)
            elif customer_detail.ticket_api == TICKETING_API_JIRA:
                self.ticketing_system = Jira(customer_detail.url, customer_detail.username, 
                                                          customer_detail.password)           
            elif customer_detail.ticket_api == TICKETING_API_CONNECTWISE: 
                self.ticketing_system = ConnectWise(customer_detail.url, customer_detail.username, 
                                                          customer_detail.password)
            elif customer_detail.ticket_api == TICKETING_API_FRESHSERVICE :
                self.ticketing_system = FreshService(customer_detail.url, customer_detail.username, 
                                                          customer_detail.password)
            elif customer_detail.ticket_api == TICKETING_API_SALESFORCE :
                self.ticketing_system = SalesForce(customer_detail.url, customer_detail.username,
                                                          customer_detail.password)
            elif customer_detail.ticket_api == TICKETING_API_SERVICENOW:
                self.ticketing_system = ServiceNow(customer_detail.url, customer_detail.username,
                                                   customer_detail.password)
            if self.ticketing_system:
                self.ticketing_system.set_mandatory_fields(customer_detail.extra_info)
                self.ticketing_system.save(case_detail)
                self.stage = 2
                ticket_number = self.ticketing_system.ticket_number
                return ticket_number
            self.corelog.error("Failed to update ticketing system for case %d. Customer: %s" % 
                          (self.incident_id, case_detail.customer_name) )
            customer_detail.print_info()
        except WebFault, f:
            self.corelog.error("Failed to update ticketing system for case %d. Fault: %s" % (self.incident_id, f.fault ))
        except Exception, e:
            self.corelog.error("Exception caught in update_ticketing_system")
            self.corelog.exception(e)
        if(self.ticketing_system and self.ticketing_system.ticket_number and len(self.ticketing_system.ticket_number) > 0):
            self.stage = 1    
        self.add_case_to_queue(customer_id=customer_detail.id,
                               customer_name=case_detail.customer_name,
                               ticket_number=ticket_number) 
        exit("Error updating ticketing system")
    
    def update_case_details_to_provider(self, case):
        try:
            self.corelog.debug("Updating case (%s) details to provider with External ID: %s" 
                               % (case.case_id, case.external_ticket) )
            caseclient = CaseClient(self.provider_configuration.url, self.provider_configuration.username, 
                                        self.provider_configuration.password)
        
            status = caseclient.update_external_ticket(case)
            if status:
                return
            self.corelog.error("Failed to update case details for case %d." % case.case_id)   
        except WebFault, f:
            self.corelog.error("Failed to update case details for case %d. Fault: %s" 
                               % (case.case_id, f.fault ))
        except Exception, e:
            self.corelog.error("Exception caught in update_case_details_to_provider.")
            self.corelog.exception(e)
        self.add_case_to_queue(customer_id=case.customer_id,
                               customer_name=case.customer_name,
                               ticket_number=case.external_ticket)
        exit("Error updating Case Details back to provider")

def main(incident_id):

    connector = Connector(incident_id)
    
    connector.initialize()

    connector.read_provider_configuration()
    
    connector.corelog.setLevel(connector.provider_configuration.loglevel)
    
    connector.read_customer_mapping()
    case_detail = connector.get_case_details_from_provider()
    
    customer_detail = connector.get_customer_details(case_detail.customer_id, case_detail.customer_name)
    
    if connector.queue.data.stage > 0 and connector.queue.data.ticket_number and len(connector.queue.data.ticket_number) > 0:
        case_detail.external_ticket = connector.queue.data.ticket_number 
        
    
    ticket_number = connector.update_ticketing_system(case_detail, customer_detail)

    if ticket_number and len(ticket_number) > 0:
        if case_detail.external_ticket is None or ( case_detail.external_ticket.lower() != ticket_number.lower() ):
            case_detail.external_ticket = ticket_number
            connector.update_case_details_to_provider(case_detail)

    connector.remove_case_from_queue()

def usage():
    print ("%s -i <incident ID>" % __file__)
    sys.exit(1)
        
if __name__ == '__main__':
    incident_id = 0
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:",["incident=", "help"])
    except getopt.GetoptError:
        usage()
    if(len(opts) <= 0):
        usage()
    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-i", "--incident"):
            incident_id = arg.strip()
    try:
        from tendo import singleton
        me = singleton.SingleInstance(flavor_id = incident_id)
    except Exception, e:
        print "Another instance of script is running. Exiting!!!"
        sys.exit(2)
    main(int(incident_id))