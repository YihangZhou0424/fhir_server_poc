"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""
import random
import uuid
from schema import Schema
from resource import Resource
from query import get_attribute_value

#
# The Collection class is analogous to a table.
# A collection has:
#   - A unique identifier
#   - A name used to store data
#   - A list of resources
#   - The state of a collection - LOADED | SAVED
#
class Collection:

    def __init__(self, name):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.resources = list()
        self.state = Schema.LOADED

    def __str__(self):
        return self.uuid + ", " + self.name + ", " + self.state

    # Add a resource to the collection.
    def add_resource(self, resource):
        self.resources.append(resource)

    # Delete a resource form the collection.
    def del_resource(self, id):
        for resource in self.resources:
            if resource.uuid == id:
                self.resources.remove(resource)
                break

    # Update a resource.
    def update_resource(self, id, res):
        for resource in self.resources:
            if resource.uuid == id:
                self.resources = res
                break

    #
    # Get a resource using its id and return the resource.
    #
    def get(self, id):
        for resource in self.resources:
            if str(resource.uuid) == str(id):
                return resource
        return False

    #
    # Search a collection using query()
    # Return a result list of resources.
    #
    def search(self, qry):
        result = list()
        i = 0
        for resource in self.resources:
            if resource.search(qry):
                result.append(resource)
        return result

    #
    # Search a collection using using a query set.
    # Each query in the set must be a match.
    # You need to consider the structure of the collection to form the query.
    # '{', '}', '[' and ']' may be left out.
    #
    def search_complex(self, query_set):
        results = list()
        for qry in query_set:
            results += self.search(qry)
        return results

    #
    # Clear the resources.
    #
    def clear(self):
        self.resources.clear()

    #
    # Load the collection from storage.
    #
    def load(self):
        dir_list = Schema.get_resource_list(self.name)
        self.resources.clear()
        for entry in dir_list:
            if entry[0] == '.':
                # Skip directories.
                continue
            r = Resource(self.name)
            r.uuid = entry
            r.state = Schema.LOADED
            r.load(entry)
            self.resources.append(r)

    #
    # Save the collection to storage.
    #
    def save(self):
        for resource in self.resources:
            print("Collection:save", resource)
            resource.save()

    #
    # Reverse the order of a collection.
    #
    def reverse(self):
        self.resources.reverse()

    #
    # Randomise the order of a collection.
    #
    def randomise(self):
        random.shuffle(self.resources)

        get_attribute_value(self.resources[1].data, "id")

    #
    # Sort a collection based on an attribute value.
    # A Bubble Sort algorithm is used.
    # THIS SORT IS TOO SLOW
    # Takes approximately 20 seconds for 1000 records
    # Takes approximately 5 minutes for 10000 records
    # TODO: Implement a faster Order algorithm - see fast_sort()
    #
    def sort(self, attribute, reverse):
        n = len(self.resources)
        swapped = False

        # Traverse through all collection resources.
        for i in range(n - 1):
            for j in range(0, n - i - 1):

                # Traverse the collection from 0 to n-i-1
                # Get the elements from the resource data.

                try:
                    # get_attribute_value is very expensive
                    a = get_attribute_value(self.resources[j].data, attribute)
                    b = get_attribute_value(self.resources[j + 1].data, attribute)
                except None:
                    print("Invalid attribute values")
                    return

                # Check a and b.
                if a is None or b is None:
                    print("Invalid attribute comparison")
                    return

                # Swap if the resource data attribute found is greater than the next element.
                if a > b:
                    swapped = True
                    self.resources[j], self.resources[j + 1] = self.resources[j + 1], self.resources[j]

            if not swapped:
                # No swapping required.
                return

            # Reverse the order if descending.
            if reverse:
                self.reverse()

    #
    # Use the python list sort method to do a very fast search.
    # This method takes orders of magnitude less time that the linear sort() method.
    # sort_key is a Resource attribute that is filled automatically.
    #
    def fast_sort(self, attribute, reverse):
        # Fill the collection's resource sort_key
        # The sort_key will have each resource's attribute for fast access.
        for r in self.resources:
            r.sort_key = get_attribute_value(r.data, attribute)

        # Sort the collection.
        self.resources.sort(key=lambda data: data.sort_key)
