#!/usr/bin/python
# soapclient.py - SOAP client class, part of BlackStratus.

"""
    Provider level access to SOAP service.
"""
import webservice.soapclient


import logging;
logger = logging.getLogger("Notification")

class CaseClient(webservice.soapclient.TrSoapClient):
    
    def __init__(self, wsdl_url, username, password):
        self.servicename = "Case"
        logger.info("Creating %s instance. url:%s,user:%s" % (self.__class__.__name__, 
                                                              wsdl_url, username))
        webservice.soapclient.TrSoapClient.__init__(self, wsdl_url, username, 
                                                             password, self.servicename)
    
    def get_case_detail(self, caseid):
        logger.info("Fetching case (%d) details from provider" % caseid)
        case_response = self.service.getCase(caseid)
        if not case_response:
            log.error("Failed to get response from webserver.")
            return None
        
        logger.info("getCase(%s) Response: Statuscode=%d. Message:%s" % 
                 (caseid, case_response.statusCode, case_response.failureMessage))
        if(case_response.statusCode != 0):
            logger.error("getCase(%s) Failed: Statuscode=%d. Message:%s" % 
                 (caseid, case_response.statusCode, case_response.failureMessage))
            return None
        else:
            #logger.info(case_response)
            return case_response.cases
    
    def update_external_ticket(self, case):
        if not case.external_ticket:
            logger.error("External ticket not found for case %s", case.case_id)
            raise Exception("External ticket not found for case %s" % case.case_id)
        
        logger.info("Updating case %s(%s) with external ticket %s for customer %s." %
                    (case.name, case.case_id, case.external_ticket, case.customer_name))
        
        caseToSave = {
                        'caseID' : case.case_id,
                        'name' : case.name,
                        'customerName' : case.customer_name,
                        'externalTicket': case.external_ticket,
                        'assignedToUser': "admin"
                    }
        caseArray = [caseToSave]
        case_response = self.service.saveCases(caseArray)
        if not case_response or len(case_response) <=0:
            log.error("Failed to get response from webserver.")
            return False
        case_response = case_response[0]
        logger.info("saveCase(%s) Response: Statuscode=%d. Message:%s" % 
                 (case.case_id, case_response.statusCode, case_response.failureMessage))
        
        if(case_response.statusCode != 0):
            logger.error("saveCase(%s) Failed: Statuscode=%d. Message:%s" % 
                 (case.case_id, case_response.statusCode, case_response.failureMessage))
            raise Exception("SaveCase Failed: %s" % case_response.failureMessage)
        return True

class CustomerClient(webservice.soapclient.TrSoapClient):
    
    def __init__(self, wsdl_url, username, password):
        self.servicename = "Customer"
        logger.info("Creating %s instance. url:%s,user:%s" % (self.__class__.__name__, 
                                                              wsdl_url, username))
        webservice.soapclient.TrSoapClient.__init__(self, wsdl_url, username, 
                                                             password, self.servicename)

       