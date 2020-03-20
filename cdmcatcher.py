import argparse
import requests
import json
import pprint
import xml.etree.ElementTree as xTree
from zeep import Client
from config import cdm
import os

CATCHERURL = "https://worldcat.org/webservices/contentdm/catcher/6.0/CatcherService.wsdl"

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
    process_add_parser.add_argument("filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to add.")

    # Delete parser
    process_delete_parser = subparsers.add_parser("delete", help="Add metadata.")
    process_delete_parser.add_argument("collection", help="The alias of the collection to modify.")
    process_delete_parser.add_argument("filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to delete.")
    
    # Edit parser
    process_edit_parser = subparsers.add_parser("edit", help="Add metadata.")
    process_edit_parser.add_argument("collection", help="The alias of the collection to modify.")
    process_edit_parser.add_argument("filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata transformations to apply.")

    # Vocabulary parser
    vocab_parser = subparsers.add_parser("vocab", help="Return controlled vocabulary terms for selected collection.")
    vocab_parser.add_argument("collection", help="The alias of the collection to return.")
    vocab_parser.add_argument("field", help="The field with the controlled vocabulary applied.")
    
    return parser.parse_args()

def main(args):
    Catcher(args).process()

    #output(result, filename=functionName + ".xml")

class Catcher:
    # Matches program argument with Catcher function:
    AVAILABLE_FUNCTIONS = {
        'catalog'   : 'getCONTENTdmCatalog',
        'collection': 'getCONTENTdmCollectionConfig',
        'terms'     : 'getCONTENTdmControlledVocabTerms',
        'add'       : 'processCONTENTdm',
        'delete'    : 'processCONTENTdm',
        'edit'      : 'processCONTENTdm'
    }

    def __init__(self, args):
        self.catcher = Client(CATCHERURL)
        self.function = Catcher.AVAILABLE_FUNCTIONS[args.action]
        self.args = args

        if(args.version):
            print("Catcher version: " + self.catcher.service.getWSVersion())

    def output(self, body, filename='output.xml'):
        with open(filename, "w+") as f:
            f.write(body)
            f.close()

    def get_params(self, metadata = None):
        valid_actions = [ 'add', 'delete', 'edit' ]
        params = { **config }
        try:
            # Add line item arguments if provided
            for key, value in self.args.items():
                if(key == 'version') or (key == 'filepath'):
                    continue
                elif (key == 'action') and not (value in valid_actions):
                    continue
                else:
                    params[key] = value
            
            if not metadata == None:
                params['metadata']['metadatalist'] = metadata
        except:
            pass
        return params
    
    def process(self):
        # Process multiple passes if file with metadata is being processed
        try:
            contents = self.args.filepath.get_contents()
            for item in contents:
                metadata = []
                for key, value in item.items():
                    metadata.append({'field' : key, 'value' : value})
                
                getattr(self, self.function)(self.get_params(metadata))
        except:
            getattr(self, self.function)(self.get_params())
    
    #TODO replace below methods with direct calls to Catcher
    def getCONTENTdmCatalog(self, params):
        self.output(self.catcher.service.getCONTENTdmCatalog(**params), "catalog.xml")
    
    def getCONTENTdmCollectionConfig(self, params):
        print("getCONTENTdmCollectionConfig")
        print(params)
    
    def getCONTENTdmControlledVocabTerms(self, params):
        print("getCONTENTdmControlledVocabTerms")
        print(params)

    def processCONTENTdm(self, params):
        print("processCONTENTdm")
        print(params)

    class FileProcessor(argparse.Action):
        ALLOWABLE_EXTENSIONS = ('json', 'xml')
        filepath = ''
        extension = ''
        contents = {}

        def __call__(self, parser, namespace, filepath, option_string=None):
            self.filepath = filepath
            self.extension = filepath[filepath.rindex(".")+1:]

            if not self.extension in self.ALLOWABLE_EXTENSIONS:
                parser.error("Filename must have a .xml or .json extension.")
            if not os.path.exists(filepath):
                parser.error("File does not exist.")

            self.set_contents()
            
            setattr(namespace, self.dest, self)
        
        def get_contents(self):
            return self.contents

        def set_contents(self):
            parser = "parse_" + self.extension
            self.contents = getattr(self, parser)(self.filepath)

        def parse_json(self, filepath):
            # Parses json, returns list of dictionaries
            with open(filepath, "r") as f:
                return json.load(f)
        
        def parse_xml(self, filepath):
            # Parses xml, returns list of dictionaries
            xml = xTree.parse(filepath).getroot()
            result = []
            for record in xml:
                # Check for valid xml structure
                if not record.tag == "record":
                    quit("Invalid XML, please refer to documentation.")
                
                # iterate through elements, add to record dictionary
                item = {}
                for elem in record:
                    item[elem.tag] = elem.text
                
                result.append(item)

            return result

if __name__ == "__main__":
    main(get_args())