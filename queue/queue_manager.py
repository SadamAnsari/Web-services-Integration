#!/usr/bin/python
import os, glob
import logging
import time

from queue import Queue;

logger = logging.getLogger("Notification")

class QueueManager:
    def __init__(self, dir_path = None):
        if not dir_path:
            self.dir_path = os.path.join("data","queue")
        else:
            self.dir_path = dir_path
    
    def prepare_filepath(self, case_id):
        return os.path.join(self.dir_path, str(case_id) + ".q")
    
    def age(self, past_time):
        current_time = time.time()
        time_delta = current_time - past_time
        age_str = ""
        if int(time_delta) > 0:
            days = int(time_delta) / 86400
            hours = int(time_delta) / 3600 % 24
            minutes = int(time_delta) / 60 % 60
            seconds = int(time_delta) % 60
            
            if days > 0:
                age_str = "%d days, " % days
            if hours > 0:
                age_str = "%s%d hours, " % (age_str, hours)
            if minutes > 0:
                age_str = "%s%d minutes, " % (age_str, minutes)
            if seconds > 0:
                age_str = "%s%d seconds " % (age_str, seconds)
        
        return age_str
              
    def get_current_queue(self):
        queue = {}
        for  filename in glob.glob(os.path.join(self.dir_path, "*.q")):
            case_id, ext = os.path.splitext(os.path.basename(filename))
            queue_item = Queue(case_id)
            queue_item.load_data()
            queue[case_id] = queue_item
        return queue
    
    def export(self):
        logger.info("exporting current queue stats.")
        if not os.path.exists(os.path.join("data","exports")):
            os.makedirs(os.path.join("data","exports"))
        filename = "queue_%s.csv" % time.strftime("%Y%m%d%H%M%S")
        filepath = os.path.join("data","exports",filename)
        with open(filepath, "w+") as casefile:
            casefile.write("Case ID,Customer ID,Customer Name,Attempts,Created,Age\n")
            for case_id, queue in self.get_current_queue().iteritems():
                casefile.write("%s,%s,%s,%s,%d,%s\n" % 
                      (queue.data.case_id, queue.data.customer_id, queue.data.customer_name.replace(","," "), 
                       queue.data.attempts, queue.data.filecreated, self.age(queue.data.filecreated)))
        logger.info("Queue Stats exported to %s location" % filepath)
        return filepath    
    
    def print_stat(self):
        logger.info("************** Printing Queue Stats **************")
        for case_id, queue in self.get_current_queue().iteritems():
            logger.info(r"Case ID: %s, Cust ID: %d, Cust Name: %s, Attempts: %s, Pending since: %s" % 
                  (queue.data.case_id, queue.data.customer_id, queue.data.customer_name, 
                   queue.data.attempts, self.age(queue.data.filecreated)))
        logger.info("**************************************************")
    