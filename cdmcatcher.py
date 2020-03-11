import argparse
import requests
from zeep import Client
from config import cdm
import fileparser

def getResultNoParam():
    return ""

def getResultBaseParams():
    params = {**config}
    return "**" + str(params)

def getResultCollectionParam():
    # Change CDMALIAS to flag value
    params = {**config, **{'collection': CDMALIAS}}
    return "**" + str(params)    

def output(body, filename='output.xml'):
    with open(filename, "w+") as f:
        f.write(body)
        f.close()

def print_dictionary(**kwargs):
    for key, value in kwargs.items():
        print(key + ": " + value)

def verify_filename(filename):
    if not filename.endswith(('.json', '.xml')):
        raise argparse.ArgumentTypeError('Filename must have a .xml or .json extension.')
    return filename

def main():
    functionName = 'getWSVersion'
    
    parser = argparse.ArgumentParser(description="%(prog)s is a python helper script for interacting with the CONTENTdm Catcher SOAP service.")

    subparsers = parser.add_subparsers()
    subparsers.add_parser("catalog", help="Return a list of collections from a CONTENTdm Server.")
    
    collection_parser = subparsers.add_parser("collections", help="Return the collection fields and their attributes")
    collection_parser.add_argument("alias", help="The alias of the collection configuration you want returned.")
    
    process_add_parser = subparsers.add_parser("add", help="Add metadata.")
    process_add_parser.add_argument("filename", action=fileparser.ValidateFile, help="XML or JSON file with transformations.")

    process_delete_parser = subparsers.add_parser("delete", help="Add metadata.")
    process_delete_parser.add_argument("filename", action=fileparser.ValidateFile, help="XML or JSON file with transformations.")
    
    process_edit_parser = subparsers.add_parser("edit", help="Add metadata.")
    process_edit_parser.add_argument("filename", action=fileparser.ValidateFile, help="XML or JSON file with transformations.")

    vocab_parser = subparsers.add_parser("terms", help="Return controlled vocabulary terms for selected collection.")
    vocab_parser.add_argument("collection", help="The alias of the collection to return.")
    vocab_parser.add_argument("field", help="The field with the controlled vocabulary applied.")
    
    parser.add_argument("-v", "--version", help="Returns current %(prog)s, Catcher, and HTTP Transfer versions.")

    args = parser.parse_args()

    #alias = args.alias

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
