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
- Add comments to codebase for ease of maintenance

## Tips and Known Issues

- When editing a record that includes a controlled vocabulary field (whether the field in question is being edited or not) and has either an apostrophe (&) or single-quote (') in the controlled vocabulary terms for that field, the edit will claim success but will not actually edit the record. Until the bug is fixed in Catcher, you must turn off Controlled Vocabulary for the field(s) in question until edits are completed.
- Ensure valid XML when submitting to Catcher--invalid XML will throw parsing errors. Numerous online validators (such as https://www.xmlvalidation.com/) exist to test your file before submitting.
- When exporting from CONTENTdm, select the Combine option for repeating and controlled vocabulary fields.
