"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""

import cli
import loader
from schema import Schema

if __name__ == '__main__':
    schema = Schema("FHIR Server POC")
    # Load the schema
    loader.load(schema)
    # Run the command line interface
    cli.cli(schema)
