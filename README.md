# (CONTENTdm-Catcher) cdm-catcher

CONTENTdm-Catcher is a python helper script for interacting with the [CONTENTdm Catcher SOAP service](https://help.oclc.org/Metadata_Services/CONTENTdm/CONTENTdm_Catcher/Guide_to_the_CONTENTdm_Catcher).

## Use

Rename `config-dist.py` to `config.py` and update contents with the following:

- url : CONTENTdm Server URL (locate at yourwebsite/utils/diagnostics) -- include the port number
- username : CONTENTdm username
- password : CONTENTdm password
- license : CONTENTdm License Code, locaed in CONTENTdm Administration > Server > About

## TO-DO

- processCONTENTdm add/edit are not performing as expected. Delete command works as intended and removes the resultant record from CONTENTdm after re-indexing
- Provide samples input files
- Flesh out README with command-line argument details