#!/usr/bin/python

#from restkit import Resource, BasicAuth, request
import requests
import webservice.restclient
from requests.auth import HTTPBasicAuth
from issue import JiraRequest, JiraComment
import logging
import json
import re
import os
from utility import add_http
from urlparse import urljoin
from datetime import date, datetime, time, timedelta
logger = logging.getLogger("Notification")
        
class Jira_API:
    API_URL = "/rest/api/2"
    CREATE_TICKET = os.path.join(API_URL, "/issue")
    @staticmethod
    def get_create_project_meta_url(project_key = None):
        if project_key:
            return Jira_API.API_URL + "/issue/createmeta?projectKeys=%s" % project_key
        return Jira_API.API_URL + "/issue/createmeta"
    
    @staticmethod
    def get_create_comment_url(issue_key):
        return Jira_API.API_URL + "/issue/%s/comment" % issue_key
    
    @staticmethod
    def get_create_project_url():
        return Jira_API.API_URL + "/issue/"
    
class Jira(webservice.restclient.TrRestClient):
    def __init__(self, server_url, username, password):
        logger.info("Creating %s instance. url : %s, user : %s" % (self.__class__.__name__, 
                                                              server_url, username))
        webservice.restclient.TrRestClient.__init__(self, server_url, username, 
                                                             password)
        self.account_id  = ""
        self.ticket_number = ""
        
    def set_mandatory_fields(self, extra_info):
        self.account_id = extra_info.account_id
        self.issuetype = extra_info.issuetype
        self.priority = extra_info.priority
        
    def get_auth_token(self):
        return HTTPBasicAuth(self.username, self.password)
    
    def get_url(self, uri_stem):
        print self.url
        print add_http(self.url)
        print urljoin(add_http(self.url), uri_stem)
        return urljoin(add_http(self.url), uri_stem)
    
    def get(self, uri_stem, response_code = 200):
        auth_token = self.get_auth_token()
        url = self.get_url(uri_stem)
        response = requests.get(url=url, auth=auth_token)
        
        logger.info("Method:GET, Response Code: %s, URL: %s" % 
                    (response.status_code, url) )
        if response.status_code != response_code:
            logger.error("Failed to get data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:GET, Response Code: %s, URL: %s" % 
                    (response.status_code, url))
        return response.json()
    
    def post(self, uri_stem, data, response_code = 200):
        auth_token = self.get_auth_token()
        url = self.get_url(uri_stem)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url=url, auth=auth_token, data=data, headers=headers)
        logger.info("Method:POST, Response Code: %s, URL: %s" % 
                    (response.status_code, url) )
        if response.status_code != response_code:
            logger.error("Failed to post data. Error Code: %s" % response.status_code)
            raise Exception("Exception caught: Method:POST, Response Code: %s, URL: %s" % 
                    (response.status_code, url))
        return response.json()
    
    def get_existing_ticket_note_list(self, ticket_id):
        ticket_note_list = []
        uri_comments = Jira_API.get_create_comment_url(issue_key=ticket_id)
        response = self.get(uri_comments)
        for comment in response.get("comments"):
            if "body" not in comment.keys():
                continue
            matchobj = re.findall("eventID\s*=\s*(\S+)", comment['body'], re.MULTILINE)
            if matchobj:
                ticket_note_list.append(matchobj[0].strip('"').upper())
        return ticket_note_list
    
    def add_ticket_notes(self, ticket_number, case):
        logger.info("Jira: Adding / Updating Ticket Notes in ticket %s for case : %s(%s)" 
                        % (ticket_number, case.name, case.case_id))
        #get list of Existing tickets
        ticket_note_list = self.get_existing_ticket_note_list(ticket_number)
        logger.info("There are currently '%d' Ticket Notes in ticket number: %s" 
                        % (len(ticket_note_list), ticket_number))
        for event_id, event in case.events.iteritems():
            if str(event_id).upper() not in ticket_note_list:
                logger.info("Event Id: %s is new in ticket %s" % 
                            ((str(event_id).upper()), ticket_number))
                jira_comment = JiraComment(str(event))
                create_comment_uri = Jira_API.get_create_comment_url(issue_key=ticket_number)
                fields = json.dumps(jira_comment, default=lambda o: o.__dict__)
                logger.info(fields)
                create_response = self.post(create_comment_uri, fields,response_code=201)
                logger.info("Jira comment added for event %s" % str(event_id).upper())
        
    def add_ticket(self, case):
        logger.info("Adding Jira ticket for case: %s" % case.case_id)
        create_uri = Jira_API.get_create_project_url()
        jira_request = JiraRequest(self.account_id)
        jira_request.prepare(title = case.get_ticket_title(max_length=250), 
                             description = case.get_ticket_description(),
                             duedate = case.get_due_date().strftime("%Y-%m-%d %H:%M:%S"),
                             issuetype = "Task")
        jira_request.print_ticket()
        fields = json.dumps(jira_request, default=lambda o: o.__dict__)
        logger.info(fields)
        create_response = self.post(create_uri, fields,response_code=201)
        return create_response['key']
    
    def save(self, case):
        if case.external_ticket and len(case.external_ticket) > 0:
            logger.info("Jira: Updating Existing Ticket: %s for case : %s(%s)" 
                        % (case.external_ticket, case.name, case.case_id))
            self.add_ticket_notes(case.external_ticket, case)
            self.ticket_number = case.external_ticket
        else:
            logger.info("Jira: Creating New Ticket for case : %s(%s)" 
                        % (case.name, case.case_id))
            self.ticket_number = self.add_ticket(case)
            self.add_ticket_notes(self.ticket_number, case)
    def get_due_date(self, delta = 72):
        delta = delta if delta > 0 else 0
        return datetime.combine(date.today(), datetime.now().time()) + timedelta(hours=delta)
    
    def load_fields(self):
        projects = []
        uri_meta = Jira_API.get_create_project_meta_url()
        response = self.get(uri_meta)
        for project in response.get('projects'):
            project_name = project.get("name")
            project_id = project.get("key")
            issue_types = []
            for issuetype in project.get('issuetypes'):
                issue_types.append(issuetype.get("name"))
            projects.append({"name" : project_name, "id" : project_id, "issuetype" : issue_types})
        return projects
        
    def test(self):
        create_uri = Jira_API.get_create_project_url()
        jira_request = JiraRequest(self.account_id)
        jira_request.prepare(title = "My Message", 
                             description = "My Desc",
                             duedate = self.get_due_date().strftime("%Y-%m-%d %H:%M:%S"))
        jira_request.print_ticket()
        fields = json.dumps(jira_request, default=lambda o: o.__dict__)
        logger.info(fields)
        create_response = self.post(create_uri, fields,response_code=201)
        print create_response['key']
#         resource = Resource(url + ('/rest/api/latest/issue/%s' % key), 
#                             pool_instance=None, filters=[self.get_auth_tiken()])
#         auth_token = self.get_auth_token()
#         print auth_token
#         resp = requests.get('http://192.168.2.222:8080' + ('/rest/api/2/issue/%s/comment' % key), 
#                             auth=auth_token)
#         print resp.status_code
#         print resp.json()
# #         if resp.status_code != 200:
#             # This means something went wrong.
#             raise ApiError('GET /tasks/ {}'.format(resp.status_code))
#         for todo_item in resp.json():
#             print('{} {}'.format(todo_item['id'], todo_item['summary']))

        