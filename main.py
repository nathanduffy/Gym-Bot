import argparse
from datetime import datetime, date
import logging
import random
import requests
from bs4 import BeautifulSoup

# Only needed to speak item notifications
import sys
import os

# Only needed if opening in web browser
import webbrowser

# Only needed if running notications (additional setup needed - only used in AWS)
#from notify_run import Notify

LOGGING_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'

# Tuples in the format of ({Item Name},{url},[{specific subitem text to search}])
# if you want to search for all subitems on a page, send an empty list
ROGUE_ITEMS_TO_WATCH = [
    #("Echo Bike", "https://www.roguefitness.com/rogue-echo-bike", []),
    #("Mil Spec Bumper Plates 45 max", "https://www.roguefitness.com/rogue-mil-echo-bumper-plates-black"),
    #("HG Bumper Plates Wide", "https://www.roguefitness.com/rogue-hg-2-0-bumper-plates")#,
    #("Color Echo Plates", "https://www.roguefitness.com/rogue-color-echo-bumper-plate"),
    #("Change Plates", "https://www.roguefitness.com/rogue-lb-change-plates"),
    #("Iron Change Plates", "https://www.roguefitness.com/york-legacy-iron-plates"),
    #("Fleck Plates", "https://www.roguefitness.com/rogue-fleck-plates"),
    #("Test Stuff", "https://www.roguefitness.com/rogue-calibrated-kg-steel-plates", ['0.25KG', '2.5KG', '0.5KG']),
    #("Steel Cast Olympic - $8.50","https://www.roguefitness.com/rogue-olympic-plates", ['1.25LB', '2.5LB', '5LB']),
    #("Steel 6 Shooter - $23",'https://www.roguefitness.com/rogue-6-shooter-olympic-plates', ['2.5LB', '5LB']),
    #("Urethene 6 Shooter - $23.50",'https://www.roguefitness.com/rogue-6-shooter-urethane-olympic-grip-plates', ['2.5LB', '5LB']),
    #("Steel Machined Olympic - $23",'https://www.roguefitness.com/rogue-machined-olympic-plates', ['2.5LB', '5LB']),
    #("Change Plates - $33.50",'https://www.roguefitness.com/rogue-lb-change-plates', ['2.5LB', '5LB']),
    #("Urethane 12 Sided - $26",'https://www.roguefitness.com/rogue-12-sided-urethane-grip-plates', ['2.5LB', '5LB']),
    #("York Legacy Steel Cast - $3.65",'https://www.roguefitness.com/york-legacy-iron-plates', ['2.5LB', '5LB'])
    ("Rogue EZ Curl Bar", "https://www.roguefitness.com/rogue-curl-bar", [])
]

# Tuples in the format of ({Item Name},{url})
REP_ITEMS_TO_WATCH = [
    #('Rep Change Plates $19', "https://www.repfitness.com/bars-plates/olympic-plates/fractional-plates/rep-lb-change-plates"),
    #('REP Iron Plates $6', "https://www.repfitness.com/bars-plates/olympic-plates/iron-plates/rep-iron-plates"),
    #('REP Urethane Coated Plates $15', "https://www.repfitness.com/bars-plates/olympic-plates/iron-plates/rep-urethane-coated-equalizers"),
    #('REP Olympic Equializers $10', "https://www.repfitness.com/bars-plates/olympic-plates/iron-plates/rep-equalizer-iron-olympic-plates"),
    #('REP V2 Rubber Coated Oly Plates $8', "https://www.repfitness.com/bars-plates/olympic-plates/iron-plates/rep-rubber-coated-olympic-plates")
    #('AB-5000 Zero Gap Adjustable Bench', "https://www.repfitness.com/rep-ab-5000"),
    #('AB-5100 Adjustable Bench', "https://www.repfitness.com/rep-ab-5100"),
    #('FB-5000 Comp Flat Bench', "https://www.repfitness.com/rep-fb-5000-competition-flat-bench")#,
    #('Iron Plates', "https://www.repfitness.com/in-stock-items/rep-iron-plates") #This will be in stock to test the bot
]

# Simple trick to look like a user checking stock
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

################################################
# Rogue specific function to check the stock of an item
# 
# name: name of the item used for logging and user notification (not searching)
# url: URL navigation to the item
# searchTerms: limit the items you care to look at when searching the page. Send an empty list if you do not care
#
# returns: A list of all of the items on the page and their availability
# [{
#   name: string
#   inStock: boolean  
# }]
################################################
def check_rogue(name, url, searchTerms):
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    details = soup.find_all(class_="grouped-item")

    returnlist = []

    for detail in details:
        detail_item = detail.find(class_="item-name").get_text()
        if searchTerms == []:
            returnlist.append({
                            "name": name + ": " + detail_item, 
                            "inStock": (detail.find(class_="item-qty") != None)
                          })
        elif any(term in detail_item for term in searchTerms):
            returnlist.append({
                            "name": name + ": " + detail_item, 
                            "inStock": (detail.find(class_="item-qty") != None)
                          })
            
    return returnlist

################################################
# Ref Fitness specific function to check the stock of an item
# 
# name: name of the item used for logging and user notification (not searching)
# url: URL navigation to the item
# searchTerms (not supported yet)
# 
# returns: A list of all of the items on the page and their availability
# [{
#   name: string
#   inStock: boolean  
# }]
################################################
def check_rep(name, url, searchTerms=[]):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    return [{
                "name": name,
                "inStock": soup.find_all(class_="availability in-stock") != []
            }]

################################################
# Notification function that will check stock of an item and if it exists, notify the user in some way
# 
# name: name of the item used for logging and user notification (not searching)
# url: URL navigation to the item
# checkMethod: the function you want to use to check the stock
# searchTerms: limit the items you care to look at when searching the page. Send an empty list if you do not care
# test_mode: if true, notification does not happen, but the result is logged
################################################
def check_for_stock(name, url, check_method, searchTerms=[], test_mode=True):
    
    stockAvailability = check_method(name, url, searchTerms)
    
    notified = False
    #notify = Notiify()

    for item in stockAvailability:
        if item['inStock']:
            message = 'New stock available for {}'.format(item['name'])
            if test_mode:
                print(message)
            else:
                logging.info(message)
                # Only want to notify once per item. Choose which notification method you want to use
                #   - webbrowser.open: opens the URL immediateley for you to purchase
                #   - os.system: MacOS will speak saying which item is in stock
                #   - notify.send: uses the notify configuration to push notifications (only used on AWS)    
                if not notified:
                    webbrowser.open_new(url+"?"+str(random.randint(1,1000)))
                    #os.system('say "There is new stock available for {}!"'.format(item["name"]))
                    #notify.send('{} is in stock: {}?{} '.format(item['name'], url, str(random.randint(1,1000))))
                    
                notified = True
        else:
            logging.info("No Stock for {}".format(item["name"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t', action='store_true', default=False)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format=LOGGING_FORMAT,
                            level=logging.INFO,
                            stream=sys.stdout)

    # Check stock for Rogue Items
    logging.info('Starting checks for Rogue (items: {})'.format(len(ROGUE_ITEMS_TO_WATCH)))
    for item_name, item_url, searchTerms in ROGUE_ITEMS_TO_WATCH:
        logging.info('Checking stock of {}'.format(item_name))
        check_for_stock(item_name, item_url, check_rogue, searchTerms, args.test)

    #Check stock for Rep Fitness Items
    logging.info('Starting checks for REP(items: {})'.format(len(REP_ITEMS_TO_WATCH)))
    for item_name, item_url in REP_ITEMS_TO_WATCH:
        logging.info('Checking stock of {}'.format(item_name))
        check_for_stock(item_name, item_url, check_rep, args.test)

if __name__ == '__main__':
    main()
