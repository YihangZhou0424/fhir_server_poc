"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""

import os.path
import uuid

from query import get_attribute_value, get_segment_attribute_value
from schema import Schema
import json

# Return the length of resource data
length = 0

# Remove whitespace reduces up to 28%
compress = 1

#
# A Resource is a collection item in the Collection resources list.
#
class Resource:
    def __init__(self, resource_type):
        self.uuid = uuid.uuid4()
        self.type = resource_type
        self.data = ""
        self.state = Schema.LOADED

    def __str__(self):
        if length:
            return str(len(self.data)) + ', ' + str(self.uuid) + ', ' + self.type + ', ' + self.data
        else:
            return str(self.uuid) + ', ' + ', ' + self.type + ', ' + self.data

    # Find the attribute value in the FHIR (json).
    def get_attribute_value(self, attribute):
        att = get_attribute_value(self.data, attribute)
        return att

    # Find the attribute in the first segment of FHIR (json).
    def get_segment_attribute_value(self, segment, attribute):
        att = get_segment_attribute_value(self.data, segment, attribute)

    # Load a resource from a file.
    def load_file(self, file_name, collection):
        try:
            path = os.path.join(collection, file_name)
            with open(path, 'r') as file:
                self.data = file.read().replace('\n', '')
            return True
        except FileNotFoundError:
            return False

    # Get an attribute's value.
    def get_attribute_value(self, attribute):
        try:
            j = json.loads(self.data)
            x = str(j[attribute]).replace("\'", "\"").replace("[", "").replace("]", "")
            return x
        except KeyError:
            return None

    # Get a segment attribute value.
    def get_segment_attribute_value(self, segment, attribute):
        try:
            part = self.get_attribute_value(segment)
            t = Resource("Segment")
            t.data = part
            result = t.get_attribute_value(attribute)
            return result
        except KeyError:
            return None

    # Test and attribute value.
    def test_attribute_value(self, attribute, operator, value):
        try:
            j = json.loads(self.data)
            x = j[attribute]
            y = value
            # If the attribute is a number then make y a number.
            if type(x) != str:
                if value.isnumeric():
                    y = float(value)

            if operator == "=":
                return x == y
            if operator == "!=":
                return x != y
            elif operator == ">":
                return x > y
            elif operator == ">=":
                return x >= y
            elif operator == "<":
                return x < y
            elif operator <= y:
                return x <= y
            else:
                return None

        except KeyError:
            return None

    # Test a segment attribute value.
    def test_segment_attribute_value(self, segment, attribute, value):
        try:
            part = self.get_attribute_value(segment)
            t = Resource("Segment")
            t.data = part
            result = t.get_attribute_value(attribute)
            if result == value:
                return True
            else:
                return False
        except KeyError:
            return None

    # Find a string in a resource.
    def search(self, qry):
        if self.data.find(qry) == -1:
            return False
        else:
            return True

    # Load a resource from storage.
    def load(self, file_name):
        try:
            t = os.path.join(Schema.ROOT, self.type)
            path = os.path.join(t, file_name)

            with open(path, 'r') as file:
                self.uuid = file_name
                if not compress:
                    self.data = file.read().replace('\n', '')
                else:
                    # Remove unnecessary whitespace.
                    # Compress the size of FHIR Patient by up to 28%
                    self.data = file.read().replace('\n', '') \
                        .replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ') \
                        .replace(' : ', ':') \
                        .replace('{ ', '{') \
                        .replace('} ', '}') \
                        .replace('" }', '"}') \
                        .replace('] }', ']}') \
                        .replace(', ', ',').replace(', ', ',')
                self.state = Schema.LOADED

        except FileNotFoundError:
            self.uuid = ""
            self.data = ""
            self.state = Schema.LOAD_ERROR
            print("Resource: Load Error")

    # Save a resource to storage.
    def save(self):
        try:
            t = os.path.join(Schema.ROOT, self.type)
            path = os.path.join(t, str(self.uuid))
            f = open(path, "w")
            f.write(self.data)
            f.close()
            self.state = Schema.SAVED
            # Bug: Reload the resource so white space is removed.
            fn = str(self.uuid)
            self.data = ""
            self.load(fn)
        except FileExistsError:
            self.state = Schema.SAVE_ERROR
            print("Resource: Save Error")