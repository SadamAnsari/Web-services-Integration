#!/usr/bin/python
# soapclient.py - SOAP client class, part of BlackStratus.

"""
    Provider level access to SOAP service.
"""
import re

import suds
from suds import WebFault
from suds.client import Client
from suds.plugin import DocumentPlugin
from suds.sax.element import Element
from suds.sax.attribute import Attribute
from suds.xsd.sxbasic import Import
import webservice.soapclient
from datetime import datetime

from utility.util import *
from customer import *
import logging

logger = logging.getLogger("Notification")

class MyPlugin(DocumentPlugin):
    """Plugin to add element to ServiceTicket, TicketNote that is not defined in WSDL."""
    def __init__(self, *args):
        self.args = args
        #print self.args
        
    def parsed(self, context):
        complexTypes = context.document.getRoot().getChild('types').getChild('schema').getChildren('complexType')
        for ct in complexTypes:
            if ct.get('name') == 'ServiceTicket' :
                s_elements1 = ct     
            if ct.get('name') == "TicketNote" :
                s_elements2 = ct
        # print "inside"        
        # print s_elements1, s_elements2
        sequenceElements1 = s_elements1.getChild('sequence')
        sequenceElements2 = s_elements2.getChild('sequence')
        #print sequenceElements1,sequenceElements2
        for key in self.args:
            # Create new element (node)
            e = suds.sax.element.Element('element')
            e.setPrefix('s')

            # Add attributes
            a = suds.sax.attribute.Attribute('minOccurs')
            a.setValue(0)
            e.append(a)
            
            a = suds.sax.attribute.Attribute('name')
            a.setValue(key)
            e.append(a)
            
            a = suds.sax.attribute.Attribute('maxOccurs')
            a.setValue(1)
            e.append(a)
            
            if key in ["Country","Severity","Impact","TaskItems","CompanyId"] :
                a = suds.sax.attribute.Attribute('type')
                a.setValue('s:string')
                e.append(a)
            elif key in ["AgreementId","TeamId","BoardID","CompanyRecId","ContactRecId","PortalTypeId"] :        
                a = suds.sax.attribute.Attribute('type')
                a.setValue('s:int')
                e.append(a)
            elif key in ["ProcessNotifications","Approved","ClosedFlag","CustomerUpdatedFlag"] :
                a = suds.sax.attribute.Attribute('type')
                a.setValue('s:boolean')
                e.append(a)
            elif key in ['EnteredDate','ClosedDate','RequiredDate','DateReqUtc','DateCreatedUtc'] :
                a = suds.sax.attribute.Attribute('type')
                a.setValue('s:dateTime')
                e.append(a)
            sequenceElements1.append(e)
            sequenceElements2.append(e)
            
class ConnectWise(webservice.soapclient.TrSoapClient):
    #def __init__(self, wsdl_url = , username, password):
    def __init__(self, wsdl_url = "", username = "", password = ""):
        
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__, 
                                                              wsdl_url, username))
#         webservice.soapclient.TrSoapClient.__init__(self, wsdl_url+self.api_url, username, 
#                                                              password)
        self.ticket_number = ""
        self.wsdl_url = wsdl_url
        self.username = username
        self.password = password
        self.ApiCredentials = None
        self.uri = "/v4_6_release/apis/1.5/"
        self.plugin = MyPlugin('Country','ProcessNotifications','AgreementId','TeamId',
                                'Severity','Impact','TaskItems','ActualHours','BoardID',
                                'EnteredDate','ClosedDate','CompanyRecId','ContactRecId',
                                'CompanyId','PortalTypeId','Approved','RequiredDate',
                                'DateReqUtc','ClosedFlag','CustomerUpdatedFlag','DateCreatedUtc')
        
        self.url = self.get_API_url(self.wsdl_url, self.uri, "ServiceTicketApi.asmx?wsdl")
        self.client = Client( self.url, plugins = [self.plugin])
        self.company_id = ""
        self.board_id = ""
        self.board_name = ""
        self.status = "N"
        self.priority = "Priority 3 - Normal Response"
      
    def get_API_url(self, wsdl_url, uri, api_name):
#         To Create  final URL  for client
        api_url = wsdl_url + uri + api_name
        return api_url
    
    def set_mandatory_fields(self, connectwise_info) :
        self.company_id = connectwise_info.company_id
        self.board_id = connectwise_info.board_id
        self.board_name = connectwise_info.board_name
#         self.status = connectwise_info.status
#         self.status_name = connectwise_info.status_name
        
        logger.info("Setting ConnectWise mandatory fields.")
        connectwise_info.print_info()
                
        self.ApiCredentials = self.client.factory.create('ApiCredentials')
        self.ApiCredentials.CompanyId = self.company_id
        self.ApiCredentials.IntegratorLoginId = self.username
        self.ApiCredentials.IntegratorPassword = self.password
#         print "api credentials: %s"%(self.ApiCredentials)
        
    def test(self, case):
        serviceTicket = self.factory.create('ServiceTicket')
        serviceTicket.TicketNumber  = 0
        serviceTicket.Board = "Professional Services"
        serviceTicket.Summary = case.message
        serviceTicket.SendingSrServiceRecid = 0
        serviceTicket.Status  =  self.status
        serviceTicket.DateReq  = "0001-01-01T00:00:00"
        serviceTicket.SubBillingMethodId  = "Actual"
        serviceTicket.SubBillingAmount = 0.00
        serviceTicket.SubDateAccepted = "0001-01-01T00:00:00"
        serviceTicket.SubDateAcceptedUtc = "0001-01-01T00:00:00"
        serviceTicket.BudgetHours = 0.00
        serviceTicket.SkipCallback = False
        serviceTicket.LastUpdateDate = datetime.now().isoformat()
#         print (serviceTicket)
#         try :
#             response = self.client.service.AddServiceTicketViaCompanyId(self.ApiCredentials,self.companyId,serviceTicket)
#             print response
#         except suds.WebFault as detail:
#             print detail     
    def add_ticket(self, case):
        logger.info("Adding ConnectWise ticket for case: %s" % case.case_id)
        serviceTicket = self.client.factory.create('ServiceTicket')
        serviceTicket.Board = self.board_name 
        serviceTicket.TicketNumber  = 0
        serviceTicket.Summary = case.get_ticket_title(max_length=100)
        serviceTicket.SendingSrServiceRecid = 0
        serviceTicket.Status = self.status
        serviceTicket.DateReq = datetime.now().isoformat()   #case.get_due_date()
        serviceTicket.Priority = self.priority
        serviceTicket.SubBillingMethodId  = "Actual" # None or Actual or FixedFee or Override or NotToExceed
        serviceTicket.SubBillingAmount = 0.00
        serviceTicket.SubDateAccepted = datetime.now().isoformat()
        serviceTicket.SubDateAcceptedUtc = datetime.now().isoformat()
        serviceTicket.BudgetHours = 0.00
        serviceTicket.SkipCallback = False
        serviceTicket.LastUpdateDate = datetime.now().isoformat()
        st_ProblemDescription = case.get_ticket_description()
        if st_ProblemDescription and len(st_ProblemDescription) > 0 :
            serviceTicket.ProblemDescription = st_ProblemDescription
        self.print_ticket(serviceTicket)
        cw_response = self.client.service.AddServiceTicketViaCompanyId(self.ApiCredentials,self.company_id,serviceTicket)
        if cw_response :
            ticket_number = cw_response.TicketNumber
            logger.info("Ticket Number %s created successfully for case : %s(%s)." %
                        (ticket_number, case.name, case.case_id))
            return str(ticket_number)
        else :
            raise Exception("Failed to created Ticket for Case %s(%s)." % 
                            (case.name, case.case_id))
            
    def get_existing_ticket_note_list(self, ticket_id):
#         code for getting the ticket_note from the ticket_id
#         logger.info("Inside get_existing_ticket_note_list function with ticket_Number: %s"%ticket_id)
        self.ticket_notes = []
        cw_response = self.client.service.GetServiceTicket(self.ApiCredentials, ticket_id)
#         logger.info("%s"% cw_response.DetailNotes[0])
        if cw_response and cw_response.DetailNotes <> "" :    
            for DetailNotes in cw_response.DetailNotes[0] :
                matchobj = re.findall("eventID\s*=\s*(\S+)", DetailNotes.NoteText, re.MULTILINE)
                if matchobj :
                    self.ticket_notes.append(matchobj[0].strip('"').lower())
        return self.ticket_notes
    
    def add_ticket_notes(self, ticket_number, case):
        logger.info("Adding / Updating Ticket Notes in ticket %s for case : %s(%s)" 
                        % (ticket_number, case.name, case.case_id))

        ticket_note_list = self.get_existing_ticket_note_list(ticket_number)
        logger.info("There are currently '%d' Ticket Notes in ticket number: %s" 
                        % (len(ticket_note_list), ticket_number))
        ticket_notes = []
        count = 0
        for event_id, event in case.events.iteritems():
            if str(event_id).lower() not in ticket_note_list:
                ticket_note = self.client.factory.create('TicketNote')
                ticket_note.Id = 0
                ticket_note.NoteText = str(event)
                ticket_note.PortalIsInternalNote = False
                ticket_note.PortalIsExternalNote = False
                ticket_note.IsPartOfDetailDescription = True
                ticket_note.IsPartOfInternalAnalysis = False
                ticket_note.IsPartOfResolution = False
                ticket_note.MemberRecID = 0
                ticket_note.ContactRecID = 0
                ticket_note.DateCreated = datetime.now().isoformat()
                ticket_notes.append(ticket_note)
#             count += 1
#             if count == 2 :    
#                 break
        if len(ticket_notes) > 0:
            ticket_notes_array =  self.get_notes_array(ticket_notes)
            logger.info("Adding %d Ticket Notes in ticket %s for case : %s(%s)" 
                        % (len(ticket_notes), ticket_number, case.name, case.case_id))
            data = self.client.service.GetServiceTicket(self.ApiCredentials, ticket_number)
            data.DetailNotes = ticket_notes_array
            result = self.client.service.UpdateServiceTicketViaCompanyId(self.ApiCredentials, self.company_id, data)
            if result :
                logger.info("Ticket Notes updated for Ticket Number: %s" % (ticket_number))                     
        else:
            logger.error("No new event found for case : %s(%s)"
                      %(case.name, case.case_id))    
        
    def get_notes_array(self, notes):
        notes_array = self.client.factory.create("ArrayOfTicketNote")
        notes_array.TicketNote = notes if isinstance(notes, list) else [notes]
        return notes_array
    
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
    
#     def delete_ticket(self,ticket_id):
#         result = self.client.service.DeleteServiceTicket(ticket_id)
#         return True
    
    def print_ticket(self, ticket):
        logger.info("Ticket Instance:: Title : '%s', DueDate : '%s', Priority : '%s', Status : '%s'"
                    % (ticket.Summary,
                       ticket.DateReq, ticket.Priority,
                       ticket.Status))   
        
    def get_status(self) :
        pass
    
    def get_priority(self) :
        pass
    