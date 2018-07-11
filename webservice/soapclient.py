#!/usr/bin/python

# soapclient.py - SOAP client class, part of BlackStratus.

"""
    Top level access to SOAP service.
"""
import suds
from suds import WebFault
from suds.client import Client
from suds.plugin import MessagePlugin
from suds.xsd.doctor import Import, ImportDoctor
import logging
from utility.util import *
from customer import *
logger = logging.getLogger("Notification")

class SoapFixer(MessagePlugin):
    def marshalled(self, context):
        # Go through every node in the document and apply the fix function
        # to patch up incompatible XML.
        context.envelope.walk(self.fix_array_elements)

    def fix_array_elements(self, element):
        if element.name == 'cases':
            # Change the "ArrayOf_tns1_CaseRequest" type to "Array"
            element.set('xsi:type', 'ns3:Array')


class TrSoapClient(Client):
    
    def __init__(self, wsdl_url, username, password, servicename = None):
        #create parser and download the WSDL document
        self.url = wsdl_url
        self.username = username
        self.password = password
        self.servicename = servicename
        if servicename:
            self.url = self.get_service_url()     
        if is_https(self.url):
            logger.info("Creating secure connection")
            from suds.transport.http import HttpAuthenticated
            http_transport = HttpAuthenticated(username=self.username, password=self.password)
        else:
            from suds.transport.http import HttpAuthenticated
            http_transport = HttpAuthenticated(username=self.username, password=self.password)
        
        #Client.__init__(self, self.url, transport=http_transport, plugins=[SoapFixer()]) # uncomment after testing
        #schema_import = Import(schema_url)
        #schema_doctor = ImportDoctor(schema_import)
    
        Client.__init__(self, self.url, transport=http_transport, plugins=[SoapFixer()]) # added for testing purpose
    def get_service_url(self):
        if(self.url.find("?service=") <= 0):
            return self.url + "?service=" + self.servicename
        return self.url
        