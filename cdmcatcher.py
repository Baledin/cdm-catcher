import argparse
import requests
import json
import xml.etree.ElementTree as xtree
import xmltodict
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

def get_args():
    parser = argparse.ArgumentParser(description="%(prog)s is a python helper script for interacting with the CONTENTdm Catcher SOAP service.")
    
    # General arguments
    parser.add_argument("-v", "--version", action='store_true', help="Returns current %(prog)s, Catcher, and HTTP Transfer versions.")
    
    # Subparsers
    subparsers = parser.add_subparsers(dest="action")

    # Catalog parser
    subparsers.add_parser("catalog", help="Return a list of collections from a CONTENTdm Server.")
    
    # Collection parser
    collection_parser = subparsers.add_parser("collections", help="Return the collection fields and their attributes")
    collection_parser.add_argument("collection", help="The alias of the collection configuration you want returned.")
    
    # Add parser
    process_add_parser = subparsers.add_parser("add", help="Add metadata.")
    process_add_parser.add_argument("collection", help="The alias of the collection to modify.")
    process_add_parser.add_argument("filepath", action=FileProcessor, help="XML or JSON filepath with metadata to add.")

    # Delete parser
    process_delete_parser = subparsers.add_parser("delete", help="Add metadata.")
    process_delete_parser.add_argument("collection", help="The alias of the collection to modify.")
    process_delete_parser.add_argument("filepath", action=FileProcessor, help="XML or JSON filepath with metadata to delete.")
    
    # Edit parser
    process_edit_parser = subparsers.add_parser("edit", help="Add metadata.")
    process_edit_parser.add_argument("collection", help="The alias of the collection to modify.")
    process_edit_parser.add_argument("filepath", action=FileProcessor, help="XML or JSON filepath with metadata transformations to apply.")

    # Vocabulary parser
    vocab_parser = subparsers.add_parser("vocab", help="Return controlled vocabulary terms for selected collection.")
    vocab_parser.add_argument("collection", help="The alias of the collection to return.")
    vocab_parser.add_argument("field", help="The field with the controlled vocabulary applied.")
    
    return parser.parse_args()

def get_params(args):
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

def main(args):
    catcher = Client(CATCHERURL)
    functionName = functions[args.action]

    if(args.version):
        print("Catcher version: " + catcher.service.getWSVersion())

    #result = getattr(self, functionName)

    #result = eval("catcher.service." + functionName + "(" + functions[functionName]() + ")")
    #output(result, filename=functionName + ".xml")
    print(args)
    print_dictionary(**get_params(vars(args)))

# Matches program argument with Catcher function:
functions = {
    'catalog'   : 'getCONTENTdmCatalog',
    'collection': 'getCONTENTdmCollectionConfig',
    'terms'     : 'getCONTENTdmControlledVocabTerms',
    'add'       : 'processCONTENTdm',
    'delete'    : 'processCONTENTdm',
    'edit'      : 'processCONTENTdm'
}

class FileProcessor(argparse.Action):
    ALLOWABLE_EXTENSIONS = ('json', 'xml')
    filepath = ''
    extension = ''
    file_contents = {}

    def __call__(self, parser, namespace, filepath, option_string=None):
        self.filepath = filepath
        self.extension = filepath[filepath.rindex(".")+1:]

        if not self.extension in self.ALLOWABLE_EXTENSIONS:
            parser.error("Filename must have a .xml or .json extension.")
        if not os.path.exists(filepath):
            parser.error("File does not exist.")
        
        setattr(namespace, self.dest, self.filepath)
    
    def get_file_contents(self):
        return self.file_contents

    def set_file_contents(self):
        parser = "parse_" + self.extension
        self.file_contents = getattr(self, parser)


    def parse_json(self):
        with open(self.filepath) as f:
            return json.load(f)
    
    def parse_xml(self):
        with open(self.filepath) as f:
            return f.test


main(get_args())