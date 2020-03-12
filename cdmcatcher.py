import argparse
import requests
from zeep import Client
from config import cdm
import os

CATCHERURL = "https://worldcat.org/webservices/contentdm/catcher/6.0/CatcherService.wsdl"
CDMALIAS = "/p17176coll1"
CDMCVFIELD = "type"

config = {
    'cdmurl': cdm['url'],
    'username': cdm['username'],
    'password': cdm['password'],
    'license': cdm['license'],
}

def getArgs():
    parser = argparse.ArgumentParser(description="%(prog)s is a python helper script for interacting with the CONTENTdm Catcher SOAP service.")
    
    # General arguments
    parser.add_argument("-v", "--version", action='store_true', help="Returns current %(prog)s, Catcher, and HTTP Transfer versions.")
    
    # Subparsers
    subparsers = parser.add_subparsers(dest="action")

    # Catalog parser
    subparsers.add_parser("catalog", help="Return a list of collections from a CONTENTdm Server.")
    
    # Collection parser
    collection_parser = subparsers.add_parser("collections", help="Return the collection fields and their attributes")
    collection_parser.add_argument("alias", help="The alias of the collection configuration you want returned.")
    
    # Add parser
    process_add_parser = subparsers.add_parser("add", help="Add metadata.")
    process_add_parser.add_argument("filepath", action=ValidateFile, help="XML or JSON filepath with metadata to add.")
    process_add_parser.add_argument("alias", help="The alias of the collection to modify.")

    # Delete parser
    process_delete_parser = subparsers.add_parser("delete", help="Add metadata.")
    process_delete_parser.add_argument("filepath", action=ValidateFile, help="XML or JSON filepath with metadata to delete.")
    
    # Edit parser
    process_edit_parser = subparsers.add_parser("edit", help="Add metadata.")
    process_edit_parser.add_argument("filepath", action=ValidateFile, help="XML or JSON filepath with metadata transformations to apply.")
    process_edit_parser.add_argument("alias", help="The alias of the collection to modify.")
    process_edit_parser.add_argument("field", nargs="+", help="The field(s) with the controlled vocabulary applied.")

    # Vocabulary parser
    vocab_parser = subparsers.add_parser("terms", help="Return controlled vocabulary terms for selected collection.")
    vocab_parser.add_argument("collection", help="The alias of the collection to return.")
    vocab_parser.add_argument("field", help="The field with the controlled vocabulary applied.")
    
    return parser.parse_args()

def getParams(args):
    valid_actions = [ 'add', 'delete', 'edit' ]
    params = { **config }
    for key, value in args.items():
        if(key == 'version') or (key == 'filepath'):
            continue
        elif (key == 'action') and not (value in valid_actions):
            continue
        else:
            params[key] = value

    return params

def output(body, filename='output.xml'):
    with open(filename, "w+") as f:
        f.write(body)
        f.close()

def print_dictionary(**kwargs):
    for key, value in kwargs.items():
        print(key + ": " + str(value))

def verify_filename(filename):
    if not filename.endswith(('.json', '.xml')):
        raise argparse.ArgumentTypeError('Filename must have a .xml or .json extension.')
    return filename

def main(args):
    catcher = Client(CATCHERURL)
    functionName = args.action

    if(args.version):
        print("Catcher version: " + catcher.service.getWSVersion())

    #result = getattr(self, functionName)

    #result = eval("catcher.service." + functionName + "(" + functions[functionName]() + ")")
    #output(result, filename=functionName + ".xml")
    print(args)
    print_dictionary(**getParams(vars(args)))

# Matches program argument with Catcher function:
functions = {
    'catalog'   : 'getCONTENTdmCatalog',
    'collection': 'getCONTENTdmCollectionConfig',
    'terms'     : 'getCONTENTdmControlledVocabTerms',
    'add'       : 'processCONTENTdm',
    'delete'    : 'processCONTENTdm',
    'edit'      : 'processCONTENTdm'
}

class ValidateFile(argparse.Action):
    EXT = ('.json', '.xml')

    def __call__(self, parser, namespace, filename, option_string=None):
        if not os.path.exists(filename):
            parser.error("File does not exist.")
        if not filename.endswith(self.EXT):
            parser.error("Filename must have a .xml or .json extension.")
        setattr(namespace, self.dest, filename)

main(getArgs())