import argparse
from config import cdm
from datetime import datetime
import json
import lxml.etree as xTree
import os
import zeep

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
    collection_parser = subparsers.add_parser("collection", help="Return the collection fields and their attributes")
    collection_parser.add_argument("alias", help="The alias of the collection configuration you want returned.")
    
    # Add parser
    process_add_parser = subparsers.add_parser("add", help="Add metadata.")
    process_add_parser.add_argument("alias", help="The alias of the collection to modify.")
    process_add_parser.add_argument("filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to add.")

    # Delete parser
    process_delete_parser = subparsers.add_parser("delete", help="Add metadata.")
    process_delete_parser.add_argument("alias", help="The alias of the collection to modify.")
    process_delete_parser.add_argument("filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to delete.")
    
    # Edit parser
    process_edit_parser = subparsers.add_parser("edit", help="Add metadata.")
    process_edit_parser.add_argument("alias", help="The alias of the collection to modify.")
    process_edit_parser.add_argument("filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata transformations to apply.")

    # Vocabulary parser
    vocab_parser = subparsers.add_parser("terms", help="Return controlled vocabulary terms for selected collection.")
    vocab_parser.add_argument("alias", help="The alias of the collection to return.")
    vocab_parser.add_argument("field", help="The field with the controlled vocabulary to return.")
    
    return parser.parse_args()

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
        self.args = vars(args)
        self.catcher = zeep.Client(CATCHERURL)
        self.function = Catcher.AVAILABLE_FUNCTIONS[self.args['action']]

        if(self.args['version']):
            print("Catcher version: " + self.catcher.service.getWSVersion())

    def output(self, body, filename='output.xml', mode="w"):
        with open(filename, mode) as f:
            if not mode[0] == "r":
                f.write(str(body))
                if mode[0] == "a":
                    f.write("\n\n")
            f.close()

    def get_params(self, metadata = None):
        valid_actions = [ 'add', 'delete', 'edit' ]
        params = { **config }
        # Add line item arguments if provided
        for key, value in self.args.items():
            if(key == 'version') or (key == 'filepath'):
                continue
            elif (key == 'action') and not (value in valid_actions):
                continue
            elif (key == 'alias'):
                # alias is known to Catcher by collection, ensure preceeding slash
                alias = value
                if not alias[0] == "/":
                    alias = "/" + alias
                params['collection'] = alias
            else:
                params[key] = value
        
        if not metadata == None:
            params['metadata'] = metadata #{'metadataList' : { 'metadata' : metadata } }
        
        return params
    
    def process(self):
        # Processes multiple passes if file with metadata is being processed or just once for no metadata
        if 'filepath' in self.args:
            contents = self.args['filepath'].get_contents()
            factory = self.catcher.type_factory('ns0')
            for item in contents:
                metadatawrapper = factory.metadataWrapper()
                
                metadata = []
                for key, value in item.items():
                    metadata.append(factory.metadata(field=key, value=value))
                
                metadatawrapper.metadataList = {'metadata' : metadata}

                getattr(self, self.function)(self.get_params(metadatawrapper))
        else:
            getattr(self, self.function)(self.get_params())
            
    
    def getCONTENTdmCatalog(self, params):
        self.output(self.catcher.service.getCONTENTdmCatalog(**params), "Catalog.xml")
    
    def getCONTENTdmCollectionConfig(self, params):
        filename = "Collection_" + params['collection'].replace('/','')
        self.output(self.catcher.service.getCONTENTdmCollectionConfig(**params), filename + ".xml")
    
    def getCONTENTdmControlledVocabTerms(self, params):
        filename = "Vocabulary_" + params['collection'].replace('/','')
        self.output(self.catcher.service.getCONTENTdmControlledVocabTerms(**params), filename + ".xml")

    def processCONTENTdm(self, params):
        filename = "Process_" + params['action'] + "_" + params['collection'].replace('/','') + ".txt"
        timestamp = "******** " + str(datetime.now()) + " ********"
        self.output(timestamp, filename, "a")
        self.output(self.catcher.service.processCONTENTdm(**params), filename, "a")

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
    Catcher(get_args()).process()