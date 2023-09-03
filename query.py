"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""
import json


#
# Query functions for Collections and Resources.
#

# Get a resource attribute value.
def get_attribute_value(resource, attribute):
    try:
        j = json.loads(resource)
        x = str(j[attribute]).replace("\'", "\"").replace("[", "").replace("]", "")
        return x
    except (KeyError, TypeError):
        return None


# Json is split into sequences or segments.
# Find the specified segments and return the attribute value.
def get_segment_attribute_value(resource, segment, attribute):
    try:
        part = get_attribute_value(resource, segment)
        result = get_attribute_value(part, attribute)
        return result
    except (KeyError, TypeError):
        return None


# Get an attribute value using segment1 and segment 2.
def get_2segments_attribute_value(resource, segment1, segment2, attribute):
    try:
        part1 = get_attribute_value(resource, segment1)
        part2 = get_attribute_value(part1, segment2)
        result = get_attribute_value(part2, attribute)
        return result
    except (KeyError, TypeError):
        return None


# Test the value of an attribute using s subset of standard binary operators.
# Determine if we comparing numbers of strings.
def test_attribute_value(resource, attribute, operator, value):
    try:
        j = json.loads(resource)
        x = j[attribute]
        y = value
        # TODO: Bug.
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
    except (KeyError, TypeError):
        return None


# Test a segment's attribute value.
def test_segment_attribute_value(resource, segment, attribute, operator, value):
    try:
        part = get_attribute_value(resource, segment)
        if part is None:
            return None
        result = test_attribute_value(part, attribute, operator, value)
        return result
    except (KeyError, TypeError):
        return None


# Test 2 segment attribute value.
def test_2segments_attribute_value(resource, segment1, segment2, attribute, operator, value):
    try:
        part1 = get_attribute_value(resource, segment1)
        part2 = get_attribute_value(part1, segment2)
        result = test_attribute_value(part2, attribute, operator, value)
        return result
    except (KeyError, TypeError):
        return None


# Test range of an attribute.
def test_attribute_range(resource, attribute, low, high):
    # Test low and high are numbers
    try:
        j = json.loads(resource)
        x = j[attribute]
        if low <= x <= high:
            return True
        else:
            return False
    except (KeyError, TypeError):
        return None


# Test the range of a segment.
def test_segment_attribute_range(resource, segment, attribute, low, high):
    try:
        part = get_attribute_value(resource, segment)
        result = test_attribute_range(part, attribute, low, high)
        return result
    except (KeyError, TypeError):
        return None


# Test the range of a segment(2) value within a segment(1).
def test_2segments_attribute_range(resource, segment1, segment2, attribute, low, high):
    try:
        part1 = get_attribute_value(resource, segment1)
        part2 = get_attribute_value(part1, segment2)
        result = test_attribute_range(part2, attribute, low, high)
        return result
    except (KeyError, TypeError):
        return None


#
# Collection Queries
#
# Get all resources that have a segment where the attribute/operator/value expression is true.
def get_resources_by_attribute_value(collection, attribute, operator, value, distinct):
    result = list()
    for resource in collection.resources:
        if test_attribute_value(resource.data, attribute, operator, value):
            result.append(resource)
            if distinct:
                return result
    return result


# Get all resources by attribute range
def get_resources_by_attribute_range(collection, attribute, low, high, distinct):
    result = list()
    for resource in collection.resources:
        if test_attribute_range(resource.data, attribute, low, high):
            result.append(resource)
            if distinct:
                return result
    return result


# Get all resources that have a segment attribute where value operator value = True
def get_resources_by_segment_attribute_value(collection, segment, attribute, operator, value):
    result = list()
    for resource in collection.resources:
        if test_segment_attribute_value(resource.data, segment, attribute, operator, value):
            result.append(resource)
    return result


def get_resources_by_2segments_attribute_value(collection, segment1, segment2, attribute, operator, value):
    result = list()
    for resource in collection.resources:
        if test_2segments_attribute_value(resource.data, segment1, segment2, attribute, operator, value):
            result.append(resource)
    return result


# Get all resources that have 2 segment attribute value range.
def get_resources_by_segment_attribute_range(collection, segment, attribute, low, high):
    result = list()
    for resource in collection.resources:
        if test_segment_attribute_range(resource.data, segment, attribute, low, high):
            result.append(resource)
    return result


# Get all resources that have segment attribute value range.
def get_resources_by_2segments_attribute_range(collection, segment1, segment2, attribute, low, high):
    result = list()
    for resource in collection.resources:
        if test_2segments_attribute_range(resource.data, segment1, segment2, attribute, low, high):
            result.append(resource)
    return result
