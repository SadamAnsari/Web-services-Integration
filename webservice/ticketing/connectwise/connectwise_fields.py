#!/usr/bin/python
import sys
from suds.client import Client
import logging
import webservice.soapclient
logger = logging.getLogger("Notification")  
       
class ConnectWiseFields(webservice.soapclient.TrSoapClient):
    
    def __init__(self, wsdl_url = "", username = "", password = "", companyId = ""):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__, 
                                                              wsdl_url, username))
#         webservice.soapclient.TrSoapClient.__init__(self, wsdl_url, username, 
#                                                         password)
        self.uri = "/v4_6_release/apis/1.5/"
        
        self.wsdl_url = wsdl_url
        self.company_id = companyId
        self.company_list = {}
        self.board_ids = {}
        self.statuses = {}
        self.username = username
        self.password = password
    
    def get_client(self, api_name):
        url = self.wsdl_url + self.uri + api_name
        client = Client(url)
        return client
    
    def get_Credentials(self, company_id, username, password, api_name):
        client = self.get_client(api_name)
        ApiCredentials = client.factory.create('ApiCredentials')
        ApiCredentials.CompanyId = company_id
        ApiCredentials.IntegratorLoginId = username
        ApiCredentials.IntegratorPassword = password
        return ApiCredentials    
    
    def load_boards_fields(self):
#         self.load_companies("ReportingApi.asmx?wsdl") 
        self.boards_fields = [self.load_boards("ReportingApi.asmx?wsdl")]
        return self.boards_fields
    
    def load_status_fields(self,board_id):
        self.status_fields  = [self.load_statuses("ReportingApi.asmx?wsdl", board_id)]
        return self.status_fields 
    
    def get_priorities(self):
        self.priorities = {
                            1 : "Priority 1 - Emergency Response",
                            2 : "Priority 2 - Quick Response",
                            3 : "Priority 3 - Normal Response",
                            4 : "Priority 4 - Scheduled Maintenance"
                        }
        return self.priorities 
   
    def load_boards(self, api_name):
        client = self.get_client(api_name)
        ApiCredentials = self.get_Credentials(self.company_id,self.username,self.password, api_name)
        response = client.service.RunReportQuery(ApiCredentials,'ServiceBoard')
        for result in response['ResultRow']:
            tmp = {}
            for field in result['Value']:
                tmp[field['_Name']] = field['value']
            self.board_ids[tmp['SR_Board_RecID']] = tmp['Board_Name']
        return self.board_ids
    
    def load_statuses(self, api_name, board_id):
#         print "inside load_statuses"
        client = self.get_client(api_name)
        ApiCredentials = self.get_Credentials(self.company_id,self.username,self.password, api_name)
        conditions = "SR_Board_RecID = '%s'"%(board_id)
        response =  client.service.RunReportQuery(ApiCredentials,'ServiceStatus', conditions)
        results = []
        if response :
          for result in response['ResultRow'] :
            tmp = {}
            for field in result['Value']:
                tmp[field['_Name']] = field['value']
            results.append(tmp)
            count = 0        
            for item in results:
                self.statuses[count] =  item['Service_Status_Desc']
                count += 1
            return self.statuses
        else:
            print "No status present for Board Id: %s \nPlease add the status to specific board."%(board_id)
            sys.exit()
