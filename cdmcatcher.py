import argparse
from datetime import datetime
import json
import lxml.etree as xTree
import os
import pprint
import zeep


def get_args():
    parser = argparse.ArgumentParser(
        description="%(prog)s is a python helper script for interacting with the CONTENTdm Catcher SOAP service.")

    # General arguments
    # TODO Add additional version calls to string
    parser.add_argument("-v", "--version", action='store_true',
                        help="Returns current %(prog)s, Catcher, and HTTP Transfer versions.")
    parser.add_argument(
        "-o", "--output", help="Filename and path for output.")

    # Subparsers
    subparsers = parser.add_subparsers(dest="action")

    # Catalog parser
    subparsers.add_parser(
        "catalog", help="Return a list of collections from a CONTENTdm Server.")

    # Collection parser
    collection_parser = subparsers.add_parser(
        "collection", help="Return the collection fields and their attributes")
    collection_parser.add_argument(
        "alias", help="The alias of the collection configuration you want returned.")

    # Add parser
    process_add_parser = subparsers.add_parser("add", help="Add metadata.")
    process_add_parser.add_argument(
        "alias", help="The alias of the collection to modify.")
    process_add_parser.add_argument(
        "filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to add.")
    process_add_parser.add_argument(
        "-cv", "--vocab", help="Allows the provision of an alternate alias and matching controlled vocabulary for X fields. Used for validating controlled vocabulary fields where the controlled vocabulary has been temporarily disabled.", nargs="+")

    # Delete parser
    process_delete_parser = subparsers.add_parser(
        "delete", help="Add metadata.")
    process_delete_parser.add_argument(
        "alias", help="The alias of the collection to modify.")
    process_delete_parser.add_argument(
        "filepath", action=Catcher.FileProcessor, help="XML or JSON filepath with metadata to delete.")

    # Edit parser
    process_edit_parser = subparsers.add_parser("edit", help="Add metadata.")
    process_edit_parser.add_argument(
        "alias", help="The alias of the collection to modify.")
    process_edit_parser.add_argument("filepath", action=Catcher.FileProcessor,
                                     help="XML or JSON filepath with metadata transformations to apply.")
    process_edit_parser.add_argument(
        "-cv", "--vocab", help="Allows the provision of an alternate alias and matching controlled vocabulary for X fields. Used for validating controlled vocabulary fields where the controlled vocabulary has been temporarily disabled.", nargs="+")

    # Vocabulary parser
    vocab_parser = subparsers.add_parser(
        "terms", help="Return controlled vocabulary terms for selected collection.")
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
        self.settings = zeep.Settings(strict=False)
        self.catcher = zeep.Client(Catcher.CATCHERURL, settings=self.settings)
        self.function = Catcher.AVAILABLE_FUNCTIONS[self.args['action']]
        self.vocab = {}

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
            if not limit is None and key in limit:
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

    # def init_vocabulary():
    # Get collection config and iterate, for each field with vocab set to 1, add to self.vocab as key
    # config = self.getCONTENTdmCollectionConfig()
    # TODO: Add controlled vocab for alt vocab if self.args.vocab == None:

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
        result += "\n"
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
            for item in contents:
                metadatawrapper = factory.metadataWrapper()

                metadata = []
                for key, value in item.items():
                    metadata.append(factory.metadata(field=key, value=value))

                metadatawrapper.metadataList = {'metadata': metadata}

                result += getattr(self, self.function)(
                    self.get_params(metadatawrapper))
        else:
            result = getattr(self, self.function)(self.get_params())

        if not result == "":
            if self.args["output"] is None:
                print(result)
            else:
                self.output(result, self.args["output"])

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
    from config import cdm

    config = {
        'cdmurl': cdm['url'],
        'username': cdm['username'],
        'password': cdm['password'],
        'license': cdm['license'],
    }
    args = get_args()
    Catcher(config, args).process()
