import argparse
from datetime import datetime
import json
import lxml.etree as et
import os
import re
import xmltodict
import zeep


def get_args():
    parser = argparse.ArgumentParser(
        description="%(prog)s is a python helper script for interacting with the CONTENTdm Catcher SOAP service.")

    # General arguments
    parser.add_argument("-v", "--version", action='store_true',
                        help="Returns current %(prog)s Catcher version.")
    parser.add_argument(
        "--output", help="Filename and path for output. Default output is to screen.")

    # Subparsers
    subparsers = parser.add_subparsers(dest="action")

    # Catalog parser
    subparsers.add_parser(
        "catalog", help="Return a list of collections from a CONTENTdm Server.")

    # Collection parser
    collection_parser = subparsers.add_parser(
        "collection", help="Return the collection fields and their attributes")
    collection_parser.add_argument(
        "alias", help="The alias of the collection configuration to return.")

    # Add parser
    process_add_parser = subparsers.add_parser("add", help="Add records to collection.")
    process_add_parser.add_argument(
        "alias", help="The alias of the collection to modify.")
    process_add_parser.add_argument(
        "filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to add.")
    process_add_parser.add_argument(
        "-cv", "--vocab", help="Allows the provision of an alternate alias and matching controlled vocabulary for X fields. Used for validating controlled vocabulary fields where the controlled vocabulary has been temporarily disabled.  Specify alternate alias and fields to validate, separated by spaces (i.e. `test_collection field1 field2 field3`).", nargs="+")

    # Delete parser
    process_delete_parser = subparsers.add_parser(
        "delete", help="Delete records from collection.")
    process_delete_parser.add_argument(
        "alias", help="The alias of the collection to modify.")
    process_delete_parser.add_argument(
        "filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to delete.")

    # Edit parser
    process_edit_parser = subparsers.add_parser("edit", help="Edit metadata for records currently existing in a collection.")
    process_edit_parser.add_argument(
        "alias", help="The alias of the collection to modify.")
    process_edit_parser.add_argument("filepath", action=Catcher.FileProcessor,
                                     help="XML or JSON filepath with metadata transformations to apply.")
    process_edit_parser.add_argument(
        "-cv", "--vocab", help="Allows the provision of an alternate alias and matching controlled vocabulary for X fields. Used for validating controlled vocabulary fields where the controlled vocabulary has been temporarily disabled.  Specify alternate alias and fields to validate, separated by spaces (i.e. `test_collection field1 field2 field3`).", nargs="+")

    # Vocabulary parser
    vocab_parser = subparsers.add_parser(
        "terms", help="Returns controlled vocabulary terms for indicated collection and field.")
    vocab_parser.add_argument(
        "alias", help="The alias of the collection to return.")
    vocab_parser.add_argument(
        "field", help="The field with the controlled vocabulary to return.")

    return parser.parse_args()


class Catcher:
    # Matches program argument with Catcher function:
    AVAILABLE_FUNCTIONS = {
        'catalog': 'get_catalog',
        'collection': 'get_config',
        'terms': 'get_vocab',
        'add': 'modify_record',
        'delete': 'modify_record',
        'edit': 'modify_record'
    }

    CATCHERURL = "https://worldcat.org/webservices/contentdm/catcher/6.0/CatcherService.wsdl"

    def __init__(self, config, args):
        self.config = config
        self.args = vars(args)
        self.catcher = zeep.Client(Catcher.CATCHERURL)
        self.function = Catcher.AVAILABLE_FUNCTIONS[self.args['action']]
        
        if not self.function == "get_catalog":
            self.init_vocabulary()

        if(self.args['version']):
            print("Catcher version: " + self.catcher.service.getWSVersion())

    def get_catalog(self, params):
        return self.catcher.service.getCONTENTdmCatalog(
            cdmurl=params['cdmurl'],
            username=params['username'],
            password=params['password'],
            license=params['license']
        )

    def get_config(self, params):
        return self.catcher.service.getCONTENTdmCollectionConfig(
            cdmurl=params['cdmurl'],
            username=params['username'],
            password=params['password'],
            license=params['license'],
            collection=params['collection']
        )

    def get_params(self, metadata=None, limit=None, config=True):
        valid_actions = ['add', 'delete', 'edit']
        if config:
            params = {**self.config}
        # Add line item arguments if provided
        for key, value in self.args.items():
            if limit is None or key in limit:
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
                params['metadata'] = metadata

        return params

    def get_vocab(self, params):
        return self.catcher.service.getCONTENTdmControlledVocabTerms(
            cdmurl=params['cdmurl'],
            username=params['username'],
            password=params['password'],
            license=params['license'],
            collection=params['collection'],
            field=params['field']
        )

    def init_vocabulary(self):
        self.vocab = {}
        config_params = self.get_params(limit=['alias'])
        config_response = self.get_config(config_params)
        fields = xmltodict.parse(config_response)

        for field in fields['fields']['field']:
            if field['vocab'] == '1':
                self.vocab[field['nickname']] = []

        # Populate alternate vocab lists if provided
        if 'vocab' in self.args and not self.args['vocab'] is None:
            alias = ("/" + self.args['vocab'].pop(0)).replace("//", "/")
            for field in self.args['vocab']:
                self.set_vocab(alias, field)

    def modify_record(self, params):
        result = "******** " + str(datetime.now()) + " ********\n"

        result += self.catcher.service.processCONTENTdm(
            action=params['action'],
            cdmurl=params['cdmurl'],
            username=params['username'],
            password=params['password'],
            license=params['license'],
            collection=params['collection'],
            metadata=params['metadata']
        )
        result += "\n\n"
        return result

    def output(self, body, filename='output.xml', mode="w"):
        with open(filename, mode, encoding="utf-8") as f:
            if not mode[0] == "r":
                f.write(body)
            f.close()

    def process(self):
        # Processes multiple passes if file with metadata is being processed or just once for no metadata
        result = ""
        if 'filepath' in self.args:
            contents = self.args['filepath'].get_contents()
            factory = self.catcher.type_factory('ns0')
            for record in contents:
                metadatawrapper = factory.metadataWrapper()

                metadata = []
                invalid_metadata = {}
                for field, value in record.items():
                    invalid_terms = self.validate_terms(field, value.split(';'))
                    if len(invalid_terms) > 0:
                        invalid_metadata[field] = invalid_terms
                    data = factory.metadata(field=field, value=value)
                    
                    # If field is dmrecord or title, move to top of list as appopriate
                    if field == 'dmrecord' and self.args['action'] in ['edit', 'delete']:
                        metadata.insert(0, data)
                    elif field == 'title' and self.args['action'] in ['add']:
                        metadata.insert(0, data)
                    else:
                        metadata.append(data)

                if len(invalid_metadata) > 0:
                    for field, value in invalid_metadata.items():
                        result += "******** " + str(datetime.now()) + " ********\n"
                        result += "Warning: " + str(value) + " does not conform to controlled vocabulary for field " + str(field) + ". Record skipped.\n"
                else:
                    metadatawrapper.metadataList = {'metadata': metadata}
                    result += getattr(self, self.function)(self.get_params(metadatawrapper))
        else:
            result = getattr(self, self.function)(self.get_params())

        if not result == "":
            if self.args["output"] is None:
                print(result)
            else:
                self.output(result, self.args["output"])

    def set_vocab(self, alias, field):
        params = self.get_params(limit=['collection', 'field'])
        params['collection'] = alias
        params['field'] = field
        vocab_result = self.get_vocab(params)

        try:
            vocab_dict = xmltodict.parse(vocab_result)
            self.vocab[field] = vocab_dict['terms']['term']
        except:
            breakpoint()
            while True:
                print("Controlled vocabulary for " + alias + "/" + field + " does not exist. Continue without checking controlled vocabulary (y/n)?")
                cont = input()
                if cont.lower() == "y":
                    break
                elif cont.lower() == "n":
                    quit("Exiting, please check alias and field are correct.")

    def validate_terms(self, field, terms):
        # Validates controlled vocabulary terms, returns empty list for all valid
        invalid_terms = []
        if field in self.vocab:
            # Initialize vocabulary if empty
            if not bool(self.vocab[field]):
                self.set_vocab(self.args['alias'], field)
            
            # Check term exists in vocabulary
            for term in terms:
                term = term.strip()
                if not term in self.vocab[field]:
                    invalid_terms.append(term)
        return invalid_terms

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
            xml = et.parse(filepath).getroot()
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
    from config import cdm

    config = {
        'cdmurl': cdm['url'],
        'username': cdm['username'],
        'password': cdm['password'],
        'license': cdm['license'],
    }
    args = get_args()
    catcher = Catcher(config, args)

    # Initialize
    catcher.process()