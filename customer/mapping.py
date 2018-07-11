#!/usr/bin/python

from customer import Customer
import logging
import csv
import os
logger = logging.getLogger("Notification")



class CustomerMapping:
    def __init__(self, mapping_file_path):
        self.KEY_ID = "id"
        self.KEY_NAME = "name"
        self.KEY_URL = "url"
        self.KEY_USERNAME = "username"
        self.KEY_PASSWORD = "password"
        self.KEY_TICKETING_API = "ticketing_api"
        self.KEY_EXTRA_INFO = "extra_info"
        self.KEY_AT_STATUS = "at_status"
        self.KEY_AT_PRIORITY = "at_priority"
        self.KEY_AT_QUEUE_ID = "at_queue"
        self.KEY_AT_ACCOUNT_ID = "at_account"
        self.mapping_file = mapping_file_path
        self.__customers = {}
        logger.info("Creating instance of CustomerMapping for file: %s" % self.mapping_file)
    
    def print_mapping(self):
        logger.info("Printing Customer Mappings")
        for customer in self.get_customers():
            customer.print_info()
    def get_customer(self, customer_id, check_wildcard = True):
        customer_id = str(customer_id)
        logger.info("get_customer called for ID: %s" % customer_id)
        if customer_id in self.__customers.keys():
            return self.__customers[customer_id]
        if check_wildcard and Customer.WILDCARD in self.__customers.keys():
            return self.__customers[Customer.WILDCARD]
        
        return None
    def add_customer(self, customer):
        logger.info("Adding customer (%s) to list." % customer.id)
        self.__customers[customer.id] = customer
        
    def get_customers(self):
        return self.__customers.values()
    
    def save_mapping(self):
        new_mapping_file = "%s_tmp" % self.mapping_file
        logger.info("Writing CustomerMapping file: %s" % self.mapping_file)
        with open(new_mapping_file, 'wb') as fp_csv:
            csv_writer = csv.writer(fp_csv, delimiter=',', lineterminator = "\n")
            data = [self.KEY_ID, self.KEY_URL, self.KEY_USERNAME, self.KEY_PASSWORD,
                    self.KEY_TICKETING_API, self.KEY_EXTRA_INFO]
            csv_writer.writerow(data)
            for customer in self.get_customers():
                data = [customer.id, customer.url, customer.username, customer.password,
                        customer.ticket_api,customer.extra_info.get_info()]
                csv_writer.writerow(data)
        if os.path.exists(self.mapping_file):
            os.rename(self.mapping_file, "%s.bak" % self.mapping_file)
            os.rename(new_mapping_file, self.mapping_file)
            os.remove("%s.bak" % self.mapping_file)
        else:
            os.rename(new_mapping_file, self.mapping_file)
            
        logger.info("Customer mapping file updated successfully.")
    def read_mapping(self):
        """ Read CSV file assuming file will have header """
        logger.info("Reading CustomerMapping file: %s" % self.mapping_file)
        if not os.path.exists(self.mapping_file):
            logger.error("CustomerMapping file (%s) not found."  % self.mapping_file)
            return
        configreader = csv.DictReader(open(self.mapping_file))
        result = {}
        for row in configreader:
            for column, value in row.iteritems():
                result.setdefault(column, []).append(value)
        if result and len(result):
            for index in range(len(result[self.KEY_ID])):
                customer =  Customer()
                customer.set(result[self.KEY_ID][index],
                                     result[self.KEY_URL][index],
                                     result[self.KEY_USERNAME][index],
                                     result[self.KEY_PASSWORD][index],
                                     int(result[self.KEY_TICKETING_API][index]),
                                     result[self.KEY_EXTRA_INFO][index]
                                     )
#             int(result[self.KEY_AT_STATUS][index]),
#             int(result[self.KEY_AT_PRIORITY][index]),
#             int(result[self.KEY_AT_QUEUE_ID][index]),
#             int(result[self.KEY_AT_ACCOUNT_ID][index]
            
                customer.print_info()
                self.__customers[customer.id.strip()] = customer
        return len(self.__customers)
            