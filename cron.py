#!/usr/bin/python
import os, getopt, sys
import logging

from queue import QueueManager, Queue
from logger import setup_logging

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    try:
        from tendo import singleton
        me = singleton.SingleInstance()
    except Exception, e:
        print "Another instance of script is running. Exiting!!!"
        sys.exit(2)
        
    try:
        setup_logging("Notification", os.path.join("data", "log"), logfile="queue.log", scrnlog = False)
        logger = logging.getLogger("Notification")
        
        logger.info("cron job initiated")
        if(len(sys.argv) <= 1):
            #process Queue
            logger.info("Processing queue")
            queue_manager = QueueManager()
            for case_id, queue_item in queue_manager.get_current_queue().iteritems():
                logger.info("Processing Queue. Case ID: %s", case_id)
                queue_item.data.print_data()
                main_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                  "main.py")
                print os.system("python '%s' -i %s" % (main_file_path, str(case_id)) )
        elif len(sys.argv) == 2:
            if(sys.argv[1].lower() == "--export"):
                logger.info("Exporting case queue")
                queue_manager = QueueManager()
                queue_manager.print_stat()
                queue_manager.export()
                
            
    except getopt.GetoptError:
        usage()