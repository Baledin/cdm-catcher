# (CONTENTdm-Catcher) cdm-catcher

CONTENTdm-Catcher is a python helper script for interacting with the [CONTENTdm Catcher SOAP service](https://help.oclc.org/Metadata_Services/CONTENTdm/CONTENTdm_Catcher/Guide_to_the_CONTENTdm_Catcher).

## Use

Rename `config-dist.py` to `config.py` and update contents with the following:

- url : CONTENTdm Server URL (locate at yourwebsite/utils/diagnostics) -- include the port number
- username : CONTENTdm username
- password : CONTENTdm password
- license : CONTENTdm License Code, locaed in CONTENTdm Administration > Server > About

## TO-DO

- Provide samples input files
- Flesh out README with command-line argument details

## Known Issues

- A known issue with Catcher (not cdm-catcher), when editing a record that includes a controlled vocabulary field and has either an apostrophe (&) or single-quote ('), the edit will claim success but will not actually edit the record. Until the bug is fixed on Catcher, you must turn off Controlled Vocabulary for the field in question until edits are completed.
