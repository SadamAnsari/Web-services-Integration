#!/usr/bin/python
import logging

logger = logging.getLogger("Notification")


class AutoTaskFields:
    def __init__(self, client):
        self.ticket_priorities = {}
        self.ticket_queue_ids = {}
        self.ticket_status = {}
        self.account_ids = {}

        self.priority_field = "Priority"
        self.queue_id_field = "QueueID"
        self.status_field = "Status"
        self.account_id_field = "AccountID"

        self.ticket_fields = {self.priority_field: self.ticket_priorities,
                              self.queue_id_field: self.ticket_queue_ids,
                              self.status_field: self.ticket_status,
                              self.account_id_field: self.account_ids}

        self.client = client

    def get_field_label(self, field_type, field_value):
        if field_type not in self.ticket_fields.keys():
            return ""
        if field_value not in self.ticket_fields[field_type].keys():
            return ""
        return " (%s) " % (self.ticket_fields[field_type][field_value])

    def load_fields(self):
        self.load_ticket_fields()
        # self.load_account_fields()
        self.fields = [self.get_autotask_fields(self.ticket_status),
                       self.get_autotask_fields(self.ticket_priorities),
                       self.get_autotask_fields(self.ticket_queue_ids)
                       ]
        return self.fields

    def load_account_fields(self, search_account):
        self.client.get_account_list(self.account_ids, search_account)
        self.fields.append(self.get_autotask_fields(self.account_ids))
        return self.account_ids

    def load_ticket_fields(self):
        try:
            field_class = "Ticket"
            logger.info("Loading field information for %s" % field_class)
            field_info = self.load_class(field_class)
            if field_info is None:
                logger.error("Failed to load Field info for %s" % field_class)
                return False

            for field in field_info[0]:
                if field.IsPickList is not True:
                    continue
                if (len(field.PicklistValues) <= 0 or len(field.PicklistValues.PickListValue) <= 0):
                    continue
                if field.Name not in self.ticket_fields.keys():
                    continue
                logger.info("Loading field details for %s::%s" % (field_class, field.Name))
                for item in field.PicklistValues.PickListValue:
                    self.ticket_fields[field.Name][int(item.Value)] = item.Label
                logger.info("Field %s::%s has %d entries" % (field_class, field.Name,
                                                             len(self.ticket_fields[field.Name].keys())))

        except Exception, e:
            logger.exception(e)
            return False
        return True

    def display(self, field_name):
        return_val = -1
        if field_name not in self.ticket_fields.keys():
            logger.error("%s field is invalid." % field_name)
            return -1
        for key, value in self.ticket_fields[field_name].iteritems():
            if return_val == -1:
                return_val = int(key)
            print "%s : %s" % (key, value)
        return return_val

    def load_class(self, field_class):
        try:
            field_info = self.client.service.GetFieldInfo(field_class)
        except Exception, e:
            logger.error("Exception caught while loading fields of %s." % field_class)
            logger.exception(e)
        return field_info

    def get_autotask_fields(self, field_dict):
        # print field_dict
        temp_dict = {}
        count = 0
        for key, value in field_dict.iteritems():
            temp_dict[count] = [key, value]
            count += 1
        return temp_dict
