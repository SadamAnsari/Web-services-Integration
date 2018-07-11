#!/usr/bin/python
import os, sys
import getpass
from customer import *
from logger import setup_logging
from bootstrap.bootinitial import *

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    try:
        from tendo import singleton
        me = singleton.SingleInstance()
    except Exception, e:
        print "Another instance of script is running. Exiting!!!"
        sys.exit(2)

    try:
        setup_logging("Notification", os.path.join("data", "log"), logfile="bootstrap.log", scrnlog=False)
        # setup_logging("suds.client", os.path.join("data", "log"), logfile="bootstrap.log", scrnlog = False)
        logger = logging.getLogger("Notification")

        customer_id = get_user_input("Enter customer ID")
        customer_name = ''
        customer_mapping_path = "customer.csv"
        customer_mapping = CustomerMapping(customer_mapping_path)
        customer_mapping.read_mapping()

        #     customer_mapping.print_mapping()
        logger.debug("Fetching customer details for ID: %s from mapping data"
                     % (customer_id))
        customer = customer_mapping.get_customer(customer_id)
        is_required = False
        if customer:
            customer.print_info(on_screen=True)
            is_required = query_yes_no("Customer detail already present. Do you want to modify it?", "no")
        else:
            logger.info("Customer Information not found.Creating new customer.")
            is_required = True
            customer = Customer()
            customer.id = customer_id

        if is_required == False:
            sys.exit();
        while True:
            # customer.name = get_user_input("Enter customer name", customer.name)
            customer.url = get_user_input("Enter Ticketing URL", customer.url)
            customer.username = get_user_input("Enter User name", customer.username)

            pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

            password, retype_password = pprompt()
            while password != retype_password:
                print('Passwords do not match. Try again')
                password, retype_password = pprompt()
            if len(password.strip()) > 0:
                customer.password = password.strip()
            print "%s : %s" % (TICKETING_API_AUTOTASK, TICKET_API[TICKETING_API_AUTOTASK])
            print "%s : %s" % (TICKETING_API_JIRA, TICKET_API[TICKETING_API_JIRA])
            print "%s : %s" % (TICKETING_API_CONNECTWISE, TICKET_API[TICKETING_API_CONNECTWISE])
            print "%s : %s" % (TICKETING_API_FRESHSERVICE, TICKET_API[TICKETING_API_FRESHSERVICE])
            print "%s : %s" % (TICKETING_API_SALESFORCE, TICKET_API[TICKETING_API_SALESFORCE])
            print "%s : %s" % (TICKETING_API_SERVICENOW, TICKET_API[TICKETING_API_SERVICENOW])
            customer.set_ticketing_api(int(get_user_input("Select ticketing API", str(
                TICKETING_API_AUTOTASK if customer.ticket_api == 0 else customer.ticket_api))))

            extra_fields = load_extra_fields(customer)
            customer_mapping.add_customer(customer)
            customer.print_info(on_screen=True, autotask_fields=extra_fields)
            is_required = query_yes_no("Please verify customer information before we save it. Do you want to save it?",
                                       "yes")
            if is_required:
                customer_mapping.save_mapping()
                break
    except Exception, ex:
        print ex
        logger.exception(ex)
