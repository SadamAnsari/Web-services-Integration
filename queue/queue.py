#!/usr/bin/python

import logging
import os

import glob
import xml.etree.cElementTree as ElementTree

logger = logging.getLogger("Notification")

QUEUE_ITEM_SEPERATOR = "###"
class QueueItem:
    def __init__(self):
        self.attempts = 0
        self.filecreated = 0
        self.case_id = ""
        self.customer_id = 0
        self.customer_name = ""
        self.stage = 0
        self.ticket_number = ""
    def print_data(self):
        logger.info("Queue Item: Customer: %s (%s), Attempts: %s, Ticket Number: %s" %
                    (self.customer_name, self.customer_id,
                     str(self.attempts), self.ticket_number))
      
class Queue:
    def __init__(self, case_id, dir_path = None):
        logger.info("Creating %s instance for incident id: %s." % (self.__class__.__name__, case_id))
        self.data = QueueItem()
        self.case_id = case_id
        
        if not dir_path:
            self.dir_path = os.path.join("data","queue")
        else:
            self.dir_path = dir_path
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        self.file_path = os.path.join(self.dir_path, str(case_id) + ".q")
        self.load_data()
        self.data.print_data()
        
#     def get_queue_data(self, file_path):
#         attempts = 0
#         customer_id = 0
#         customer_name = ""
#         try:
#             if os.path.exists(file_path):
#                 with open(file_path, "r") as casefile:
#                     line = casefile.readline()
#                     elements = line.split(QUEUE_ITEM_SEPERATOR)
#                     if(elements and len(elements) >= 3):
#                         if unicode(elements[0]).isnumeric():
#                             attempts = int(elements[0])
#                         else:
#                             logger.error("Garbage data (%s) found in queue file %s"
#                                          % (line, file_path))
#                         if unicode(elements[1]).isnumeric():
#                             customer_id = int(elements[1])
#                         else:
#                             logger.error("Garbage data (%s) found in queue file %s"
#                                          % (line, file_path))
#                         customer_name = elements[2]
#                         
#         except Exception, e:
#             logger.exception("Failed to get exception information for file %s" % file_path, e)
#             
#         return (attempts, customer_id, customer_name)
#     
#     def get_attempt(self, file_path):
#         attempts = 0
#         try:
#             if os.path.exists(file_path):
#                 with open(file_path, "r") as casefile:
#                     line = casefile.readline()
#                     elements = line.split(QUEUE_ITEM_SEPERATOR)
#                     if(elements and len(elements) > 0):
#                         if unicode(elements[0]).isnumeric():
#                             attempts = int(elements[0])
#                         else:
#                             logger.error("Garbage data (%s) found in queue file %s"
#                                          % (line, file_path))
#         except Exception, e:
#             logger.exception("Failed to get attempt details for file %s" % file_path, e)
#             
#         return attempts
    def parse_node(self, element, item_text, default_value = ""):      
        item_node = element.findall(item_text)
        if item_node and len(item_node) > 0:
            return   item_node[0].text
        return str(default_value)
    
    def load_data(self):
        if not os.path.exists(self.file_path):
            return
        try: 
            tree = ElementTree.parse(self.file_path)
            if not tree:
                return
            
            root_node = ElementTree.parse(self.file_path).getroot()
            if not root_node:
                return
            
            self.data.attempts = int( self.parse_node(root_node, "attempt", 0) )
            self.data.customer_id = self.parse_node(root_node, "cid")
            self.data.customer_name = self.parse_node(root_node, "cname")
            self.data.stage = int(self.parse_node(root_node, "stage", 0))
            self.data.ticket_number = self.parse_node(root_node, "ticket")
            self.data.filecreated = os.path.getctime(self.file_path)
            self.data.case_id = self.case_id
        except Exception, ex:
            logger.exception(ex)
        
    def write_data(self):
        root = ElementTree.Element("queue")
        
        ElementTree.SubElement(root, "attempt").text = str(self.data.attempts)
        ElementTree.SubElement(root, "cid").text = str(self.data.customer_id)
        ElementTree.SubElement(root, "cname").text = str(self.data.customer_name)
        ElementTree.SubElement(root, "stage").text = str(self.data.stage)
        ElementTree.SubElement(root, "ticket").text = str(self.data.ticket_number)
        
        tree = ElementTree.ElementTree(root)
        tree.write(self.file_path)
        
    def add(self, customer_id, customer_name, ticket_number, stage):
        
        logger.error("Adding  Case (%d) for customer %s (%s) in queue at %s stage"
                                          % (self.case_id, customer_name, customer_id, stage))
        self.data.attempts = self.data.attempts + 1
        self.data.customer_id = customer_id
        self.data.customer_name = customer_name
        self.data.stage = stage
        self.data.ticket_number = ticket_number
        self.write_data()
     
    def remove(self, case_id):
        logger.info("Removing case %s from queue." % 
                               (self.case_id))
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
