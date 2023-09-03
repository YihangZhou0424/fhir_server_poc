"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""
import os
import uuid

#
# A schema defines the database schema.
# Collections and Resources are stored in a directory structure.
#   Collection
#       <Collection Name>
#       <Collection Name>
#       ...
#

class Schema:
    # State of resource
    LOADED = "loaded"
    SAVED = "Saved"
    LOAD_ERROR = "LoadError"
    SAVE_ERROR = "SaveError"

    # Root locations of fhir resources
    ROOT = "Collection"

    def __init__(self, name):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.version = "0.2"
        self.author = "Tim Hastings (C), 2023"
        self.collections = list()
        self.number_of_results = 10
        self.state = Schema.LOADED

    def __str_(self):
        return self.uuid + ", " + self.name + ", " + self.version + ", " + self.author + ", " + self.state

    # Get a collection by name
    def get_collection(self, name):
        for collection in self.collections:
            if collection.name == name:
                return collection
        return None

    # Get collection resource list.
    def get_resource_list(self):
        path = t = os.path.join(Schema.ROOT, self)
        dir_list = os.listdir(path)
        return dir_list

    # Search a list of collections with a query list.
    def search(self, collectionList, query_list):
        results = list()
        for collection in collectionList:
            results += collection.search_complex(query_list)
        return results