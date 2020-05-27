# (CONTENTdm-Catcher) cdm-catcher

CONTENTdm-Catcher is a python helper script for interacting with the [CONTENTdm Catcher SOAP service](https://help.oclc.org/Metadata_Services/CONTENTdm/CONTENTdm_Catcher/Guide_to_the_CONTENTdm_Catcher).

CONTENTdm-Catcher allows all primary functions of the Catcher service, including add, edit, and delete functions and will automatically check metadata against controlled vocabularies.

## Use

### Install
Run `python -m pip install -r requirements.txt` from the project folder to install dependencies.

### Configure

Rename `config-dist.py` to `config.py` and update contents with the following:

- url : CONTENTdm Server URL (locate at yourwebsite/utils/diagnostics) -- include the port number
- username : CONTENTdm username
- password : CONTENTdm password
- license : CONTENTdm License Code, locaed in CONTENTdm Administration > Server > About

### Process

cdm-catcher can be used from the command line by typing `python cdmcatcher.py [general arguments] [action] [action arguments]` using the following argument details.

### General arguments

| Flag | Argument    | Comments                                                         |
| :--: | ----------- | ---------------------------------------------------------------- |
| `-h` | `--help`    | Prints the help documentation for CONTENTdm-Catcher              |
| `-v` | `--version` | prints the current OCLC Catcher version being used by the script |
|      | `--output`  | Filename and path for output. Default output is to screen.       |

### Actions

#### Catalog action

Output a list of collections from a CONTENTdm Server. Use `python cdmcatcher.py catalog`.

| Flag | Argument | Comments                |
| :--: | -------- | ----------------------- |
|      |          | No additional arguments |

#### Collection action

Output the collection fields and their attributes (XML). Use `python cdmcatcher.py collection [alias]`.

| Flag | Argument | Comments                                             |
| :--: | -------- | ---------------------------------------------------- |
|      | `alias`  | The alias of the collection configuration to return. |

#### Terms action

Output controlled vocabulary terms for indicated collection and field (XML). Use `python cdmcatcher.py terms [alias] [field]`.

| Flag | Argument | Comments                                            |
| :--: | -------- | --------------------------------------------------- |
|      | `alias`  | The alias of the collection to return.              |
|      | `field`  | The field with the controlled vocabulary to return. |

#### Add action

Add records to collection. Use `python cdmcatcher.py add [alias] [filepath] [optional arguments]`.

| Flag | Argument   | Comments                                                                                                                                                                                                                                                                                                                                                        |
| :--: | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|      | `alias`    | The alias of the collection to modify.                                                                                                                                                                                                                                                                                                                          |
|      | `filepath` | XML or JSON filepath with metadata to add.                                                                                                                                                                                                                                                                                                                      |
|      | `--vocab`  | Allows the provision of an alternate alias and matching controlled vocabulary for a list of fields. Used for validating controlled vocabulary fields where the controlled vocabulary has been temporarily disabled (see Known Issues below). Specify alternate alias and fields to validate, separated by spaces (i.e. `test_collection field1 field2 field3`). |

#### Delete action

Delete records from collection. Use `python cdmcatcher.py delete [alias] [filepath]`.

| Flag | Argument   | Comments                                      |
| :--: | ---------- | --------------------------------------------- |
|      | `alias`    | The alias of the collection to modify.        |
|      | `filepath` | XML or JSON filepath with metadata to delete. |

#### Edit action

Edit metadata for records currently existing in a collection. Use `python cdmcatcher.py edit [alias] [filepath] [optional arguments]`.

| Flag | Argument   | Comments                                                                                                                                                                                                                                                                                                                                                        |
| :--: | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|      | `alias`    | The alias of the collection to modify.                                                                                                                                                                                                                                                                                                                          |
|      | `filepath` | XML or JSON filepath with metadata to edit.                                                                                                                                                                                                                                                                                                                     |
|      | `--vocab`  | Allows the provision of an alternate alias and matching controlled vocabulary for a list of fields. Used for validating controlled vocabulary fields where the controlled vocabulary has been temporarily disabled (see Known Issues below). Specify alternate alias and fields to validate, separated by spaces (i.e. `test_collection field1 field2 field3`). |

### Metadata

Add/delete/edit calls require passing XML or JSON files to CONTENTdm-Catcher for processing.

- Metadata can consist of any number of records and (except for Delete action) any number of fields. Delete actions should only consist of the 'dmrecord' field.
- Catcher will not create new fields on the fly, fields must map to field nicknames for your collection.
- Add actions require the 'title' field, Edit and Delete actions require 'dmrecord'.
- Fields with controlled vocabularies may include multiple terms separated by semicolons (i.e. 'Animals; Animal behavior').
- Except for required fields (above), it is not necessary to include empty fields or fields not currently being edited.

#### JSON

```
[
  {
    "dmrecord": "12",
    "title": "Cat",
    "subjec": "Animals",
    "field1" : "test content 1",
    "field2" : "test content 2"
  },
  {
    "dmrecord": "13",
    "title": "Dog",
    "subjec": "Animals; Animal behavior",
    "field1" : "test content 1",
    "field2" : "test content 2"
  }
]
```

#### XML

```
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <record>
    <dmrecord>12</dmrecord>
    <title>Cat</title>
    <subjec>Animals</subjec>
    <field1>test content 1</field1>
    <field2>test content 2</field2>
  </record>
  <record>
    <dmrecord>13</dmrecord>
    <title>Dog</title>
    <subjec>Animals; Animal behavior</subjec>
    <field1>test content 1</field1>
    <field2>test content 2</field2>
  </record>
</metadata>
```

## Tips and Known Issues

- When editing a record that includes a controlled vocabulary field (whether the field in question is being edited or not) and has either an apostrophe (&) or single-quote (') in the controlled vocabulary terms for that field, the edit will claim success but will not actually edit the record. Until the bug is fixed in Catcher, you must turn off Controlled Vocabulary for the field(s) in question until edits are completed.
- Ensure valid XML when submitting to Catcher--invalid XML will throw parsing errors. Numerous online validators (such as https://www.xmlvalidation.com/) exist to test your file before submitting.
- When exporting from CONTENTdm, select the Combine option for repeating and controlled vocabulary fields.

## TO-DO

- Provide ability to use -v flag with no other arguments
- Add comments to codebase for ease of maintenance
