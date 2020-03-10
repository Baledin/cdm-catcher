# (CONTENTdm-Catcher) cdm-catcher

CONTENTdm-Catcher is a python helper script for interacting with the [CONTENTdm Catcher SOAP service](https://help.oclc.org/Metadata_Services/CONTENTdm/CONTENTdm_Catcher/Guide_to_the_CONTENTdm_Catcher).

## Use

Rename `config-dist.py` to `config.py` and update contents with the following:

- url : CONTENTdm Server URL (locate at yourwebsite/utils/diagnostics) -- include the port number
- username : CONTENTdm username
- password : CONTENTdm password
- license : CONTENTdm License Code, locaed in CONTENTdm Administration > Server > About

## TO-DO

- Implement command line arguments, script usage is currently hard-coded for testing
- Build input parser (JSON/XML) for add/edit/delete
