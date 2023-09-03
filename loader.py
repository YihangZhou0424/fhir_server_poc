"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""
import os
from datetime import datetime

from collection import Collection

#
# Load the Schema.
#
def load(schema):
    try:
        # Get the start time.
        start = datetime.now()
        schema.collections.clear()
        dirs = os.walk(schema.ROOT)
        for directory in dirs:
            entry = directory[0].split('/')
            if len(entry) > 1:
                print("Loading", entry[1])
                collection = Collection(entry[1])
                collection.load()
                schema.collections.append(collection)

        # Find the start to end time difference and display.
        end = datetime.now()
        td = (end - start).total_seconds() * 10 ** 3
        print(f"Processed in: {td:.02f} ms")

    except FileNotFoundError:
        print("Error: Cannot find schema root directory.")
        print("Create a root directory called Collection.")
        print("Each collection is a sub directory and resources are files within the collection.")
        exit(0)
    print("Ready")

