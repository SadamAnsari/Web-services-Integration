#!/usr/bin/python
import logging
logger = logging.getLogger("Notification")

class Project:
    def __init__(self):
        self.key = ""
class EntityType:
    def __init__(self):
        self.name = ""
class Fields:
    def __init__(self):
        self.project = Project()
        self.summary = ""
        self.description = ""
        self.issuetype = EntityType()
        self.duedate = ""
    
class JiraRequest:
    def __init__(self, account_id):
        self.fields = Fields()
        self.fields.project.key = account_id
        
    def prepare(self, title, description = "", issuetype = "Task", priority = "High", duedate = ""):
        self.fields.summary = title
        self.fields.description = description
        self.fields.issuetype.name = issuetype
        self.fields.duedate = duedate
    
    def print_ticket(self):
        logger.info("JiraRequest:: Project:%s, Title:%s, Description: %s, IssueType: %s, DueDate:%s" % 
                        (
                             self.fields.project.key,
                             self.fields.summary,
                             self.fields.description,
                             self.fields.issuetype.name,
                             self.fields.duedate
                         )

                 )
class AddComment:
    def __init__(self):
        self.body = ""
        
class Comment:
    def __init__(self, comment):
        self.add = AddComment()
        self.add.body = comment
        
class JiraComment:
    def __init__(self, comment):
        self.body = comment
        #self.comment = Comment(comment)