import argparse
import requests
from zeep import Client
from config import cdm

def getResultNoParam():
    return ""

def getResultBaseParams():
    params = {**config}
    return "**" + str(params)

def getResultCollectionParam():
    # Change CDMALIAS to flag value
    params = {**config, **{'collection': CDMALIAS}}
    return "**" + str(params)    

def print_dictionary(**kwargs):
    for key, value in kwargs.items():
        print(key + ": " + value)

def output(body, filename='output.xml'):
    with open(filename, "w+") as f:
        f.write(body)
        f.close()

def main():
    functionName = 'getCONTENTdmCatalog'
    
    # argParser = argparse.ArgumentParser(description="%(prog)s is a general broken link checker. Returns a list of broken URLs, their parent URL, and number of instances on the parent page.")
    # argParser.add_argument("url", nargs="+", help="The URL(s) which will be the starting point for crawling to DEPTH levels deep.")

    catcher = Client(CATCHERURL)

    print("Catcher version: " + catcher.service.getWSVersion())
    result = eval("catcher.service." + functionName + "(" + functions[functionName]() + ")")
    output(result, filename=functionName + ".xml")

CATCHERURL = "https://worldcat.org/webservices/contentdm/catcher/6.0/CatcherService.wsdl"
CDMALIAS = "/p17176coll1"
CDMCVFIELD = "type"

config = {
    'cdmurl': cdm['url'],
    'username': cdm['username'],
    'password': cdm['password'],
    'license': cdm['license'],
}

# Available calls:
functions = {
    'getWSVersion' : getResultNoParam,
    'getCONTENTdmCatalog' : getResultBaseParams,
    'getCONTENTdmCollectionConfig' : getResultCollectionParam,
    'getCONTENTdmControlledVocabTerms' : 'base,coll,field',
    'processCONTENTdm' : 'action(add,edit,delete),base,coll,data', #251, 311, 363
    'getCONTENTdmHTTPTransferVersion' : 'base,coll'
}

main()
