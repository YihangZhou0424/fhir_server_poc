FHIR Proof of Concept
Tim Hastings, 2023

Files:
cli.py          Command Line Interface - processes SQL-like commands
collection.py   Defines a database collection class.
loader.py       Loads collections from the file system.
main.py         Creates and loads the database.
order_cli.py    Example order collection command to used as a template for new commands
query.py        Underlying FHIR (json) queries.
resource.py     Defines a basic resource used in the database.
schema.py       Defines a database schema.
test.py         Used only for initial development.
test.txt        Instructions to build a database and run sample tests.

Test Data:
Patient0.FHIR   Sample patient with id = 0
Patient1.FHIR   Sample patient with id = 1
Patient2.FHIR   Sample patient with id = 2
Patient3.FHIR   Sample patient with id = 3
Patient4.FHIR   Sample patient with id = 4
Patient5.FHIR   Sample patient with id = 5
Observation1.FHIR   Sample observation with id = 1
Observation2.FHIR   Sample observation with id = 1

Notes:
Use the help command to get started.
A Collection Directory must exist in the program directory.
See test.txt to build a database and run sample tests.

Use the create command to create your own collections.
Use insert file <filename> into <collection> to add resources.
Use load n <filename> into <collection> to add many resources.

References:
https://www.hl7.org/fhir/index.html
For examples go to https://www.hl7.org/fhir/resourcelist.html
FHIR Server POC.pptx