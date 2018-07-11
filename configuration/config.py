#!/usr/bin/python

import logging
from logger import get_loglevel
import csv
import os
from utility.util import add_http

logger = logging.getLogger("Notification")


class ProviderConfiguration:
    
    def __init__(self):
        logger.info("Creating instance of ProvideConfiguration")
        self.url = ""
        self.username = ""
        self.password = ""
        self.loglevel = logging.DEBUG
        self.customer_mapping_path = ""
        
        self.KEY_USERNAME = "user"
        self.KEY_PASSWORD = "password"
        self.KEY_URL = "server"
        self.KEY_LEVEL = "log_level"
        self.KEY_CUSTOMER_CILE = "cusotmer_mapping"
        
        self.configuration_file_path = "config.csv"
        
    def read_csv_configuration(self):
        logger.info("Reading ProvideConfiguration from %s" % self.configuration_file_path)
        if not os.path.exists(self.configuration_file_path):
            logger.error("File (%s) not found."  % self.configuration_file_path)
            return
        configreader = csv.DictReader(open(self.configuration_file_path))
        result = {}
        for row in configreader:
            for column, value in row.iteritems():
                result.setdefault(column, []).append(value)
           
        if(self.KEY_URL in result.keys()):
            self.url = add_http(result.get(self.KEY_URL)[0])
        if(self.KEY_USERNAME in result.keys()):
            self.username = result.get(self.KEY_USERNAME)[0]
        if(self.KEY_PASSWORD in result.keys()):
            self.password = result.get(self.KEY_PASSWORD)[0]
        if(self.KEY_LEVEL in result.keys()):
            self.loglevel = get_loglevel(result.get(self.KEY_LEVEL)[0])
        if(self.KEY_CUSTOMER_CILE in result.keys()):
            self.customer_mapping_path = result.get(self.KEY_CUSTOMER_CILE)[0]
        if(self.customer_mapping_path is None or len(self.customer_mapping_path) <= 0):
            self.customer_mapping_path = "customer.csv"
        self.print_configuration()
                    
    def read_configuration(self, path_working_dir):
        self.configuration_file_path = os.path.join(path_working_dir, self.configuration_file_path)
        self.read_csv_configuration()
        
    def print_configuration(self):
        logger.info("ProviderConfiguration. url:%s, user:%s, password=******, loglevel:%d, customer_mapping: %s"
              % (self.url, self.username, self.loglevel, self.customer_mapping_path))