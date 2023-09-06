"""
FHIR Server Proof of Concept
Author: Tim Hastings, 2023
"""
import os
from datetime import datetime

from order_cmd import order_collection
from query import *
from collection import Collection
from resource import Resource
from schema import Schema

HELP = \
    "Commands (include spacing)\n" + \
    "--------------------------\n" + \
    "help\n" + \
    "info\n" + \
    "exit\n" + \
    "create <collection>\n" + \
    "results = n\n" + \
    "history\n" + \
    "clear\n" + \
    "reverse <collection>\n" + \
    "randomise <collection>\n" + \
    "select <qualifier> from <collection_list>\n" + \
    "select <qualifier> from <collection_list> where <attribute> <operator> <value>\n" + \
    "select <qualifier> from <collection_list> where <attribute> = <value> : <value>\n" + \
    "select <qualifier> from <collection_list> where <segment> <attribute> <operator> <value>\n" + \
    "select <qualifier> from <collection_list> where <segment> <attribute> = <value> : <value>\n" + \
    "select <qualifier> from <collection_list> where <segment1> with <segment2> <attribute> <operator> <value>\n" + \
    "select <qualifier> from <collection_list> where <segment1> with <segment2> <attribute> = <value> : <value>\n" + \
    "selectDistinct <qualifier> from <collection_list> where <attribute> <operator> <value>\n" + \
    "<qualifier>:: *|id|data|count\n" \
    "<collection_list>:: <collection>[,<collection>]\n " \
    "<operator>:: =|!=|>|>=|<|<=\n" + \
    "get <id> from <collection>\n" + \
    "insert json <json> into <collection> \n" + \
    "insert file <filename> into <collection>\n" + \
    "update <collection> json <json> where id = <id>\n" + \
    "update <collection> file <filename> where id = <id>\n" + \
    "copy <collection> to <collection>\n" + \
    "load n <filename> into <collection>"

COMMAND_INDEX = 0
QUALIFIER_INDEX = 1
FROM_INDEX = 2
COLLECTION_INDEX = 3
WHERE_INDEX = 4


#
# Function to support json with spaces.
# Future use.
#
def get_json(line):
    result = ""
    start = line.find("{")

    end = line.rfind("}")

    for i in range(start, end + 1):
        if line[i] == " ":
            result += "^"
        else:
            result += line[i]

    return result


#
# Command Line interface.
# Interpret a command line and process SQL-like functions.
# To ease complexity the command line has positional arguments
#
def cli(schema):
    create_results_collection(schema)
    while True:
        # command line used for positional arguments
        line = input("> ")
        command_line = line.split(" ")
        if len(command_line) > 0:
            command = command_line[COMMAND_INDEX]
            # Get the start time.
            start = datetime.now()
            if command == "help":
                display_help()
            elif command == "info":
                display_info(schema)
            elif command == "exit":
                exit(0)
            elif command == "create":
                create_collection(schema, command_line)
            elif command == "remove":
                print("TBA")
            elif command == "results":
                set_number_of_results(schema, command_line)
            elif command == "history":
                display_results(schema)
            elif command == "clear":
                clear_results(schema)
            elif command == "select":
                select(schema, command_line, False)
            elif command == "selectDistinct":
                select(schema, command_line, True)
            elif command == "get":
                get_resource_by_id(schema, command_line)
            elif command == "insert":
                insert_resource(schema, command_line)
            elif command == "update":
                update_resource(schema, command_line)
            elif command == "copy":
                copy_collection(schema, command_line)
            elif command == "load":
                load(schema, command_line)
            elif command == "reverse":
                reverse_collection(schema, command_line)
            elif command == "randomise":
                randomise_collection(schema, command_line)
            #
            #   New Commands
            #   Place functions in new file
            #   Add import at the top of this file.
            #
            elif command == "order" or "orderFast":
                order_collection(schema, command_line)
            else:
                print("Unknown command")

            # Find the start to end time difference and display.
            end = datetime.now()
            td = (end - start).total_seconds() * 10 ** 3
            print(f"Processed in: {td:.02f} ms")


#
# Set the number of results returned by a select statement.
#
def set_number_of_results(schema, command_line):
    try:
        n = int(command_line[2])
        if n > 0:
            schema.number_of_results = int(command_line[FROM_INDEX])
            print(schema.number_of_results)
        else:
            print("Invalid number of results")
    except ValueError:
        print("Result number must be a number")
    except IndexError:
        print("Missing number of results to be displayed")


#
# Print the results of a select query.
#
def print_select(schema, query, results):
    if results is None:
        print("Unknown collection")
        return

    if query[QUALIFIER_INDEX] == "count":
        print(str(len(results)))
        return

    n = 0
    temp_results = schema.get_collection("Result")
    if temp_results is None:
        print("Invalid Collection")
        return

    command = ">> "
    for token in query:
        command += token + " "

    qualifier = query[QUALIFIER_INDEX]
    for resource in results:
        if qualifier == "*":
            print(resource)
            temp_results.resources.append(resource)
        elif qualifier == "id":
            print(resource.uuid)
            temp_results.resources.append(resource.uuid)
        elif qualifier == "data":
            print(resource.data)
            temp_results.resources.append(resource.uuid)
        else:
            print("print_select(): Invalid select qualifier")
            return

        n += 1
        if n >= schema.number_of_results:
            break


def is_qualifier(qualifier):
    if qualifier == "*" or qualifier == "data" or qualifier == "id" or qualifier == "count":
        return True
    return False


# =|!=|>|>=|<|<=
def is_operator(operator):
    if operator == "=" or operator == "!=" or operator == ">" or \
            operator == ">=" or operator == "<" or operator == "<=":
        return True
    return False


def is_range_operator(rng):
    if rng != ":":
        print("Invalid range operator", rng)
        return False
    return True


def is_valid_range(low, high):
    try:
        lo = float(low)
        hi = float(high)
        if lo <= hi:
            return True
        else:
            print("Invalid Range - low value must be less than or equal to high value")
        return False
    except (TypeError, ValueError):
        print("Invalid Range - not a number")
        return False


def is_valid_select(query):
    if len(query) < 4:
        print("Invalid select clause - too few arguments")
        return False
    if (query[COMMAND_INDEX] == "select" or query[COMMAND_INDEX] == "selectDistinct") and is_qualifier(
            query[QUALIFIER_INDEX]) and query[FROM_INDEX] == "from":
        return True
    print("Invalid select clause qualifier")
    return False


def is_valid_collection(collection):
    if collection is None:
        print("Invalid Collection")
        return False
    return True


def is_validate_where(query):
    if query[WHERE_INDEX] != "where":
        print("Invalid where clause")
        return False
    return True


#
# Process a select query.
#
def select(schema, query, distinct):
    if not is_valid_select(query):
        return

    # Build a comma separated collection list.
    collections = list()
    if query[COMMAND_INDEX].find(','):
        collections = query[COLLECTION_INDEX].split(',')
    else:
        collections.append(query[COLLECTION_INDEX])

    if len(query) == 4:
        # select <qualifier> from <collection_list>
        for collection_name in collections:
            collection = schema.get_collection(collection_name)

            if not is_valid_collection(collection):
                return

            if query[QUALIFIER_INDEX] == "count":
                print(len(collection.resources))
            else:
                print_select(schema, query, collection.resources)

    elif len(query) == 5:
        print("Invalid command")
        return
    elif len(query) == 8:
        # select <qualifier> from <collection_list> where <attribute> = <value>
        for collection_name in collections:
            collection = schema.get_collection(collection_name)
            if not is_valid_collection(collection):
                return
            if not is_validate_where(query):
                return
            attribute = query[5]
            operator = query[6]
            if not is_operator(operator):
                return
            value = query[7]
            results = get_resources_by_attribute_value(collection, attribute, operator, value, distinct)
            print_select(schema, query, results)

    elif len(query) == 9:
        # get <qualifier> from <collection_list> where <segment> <attribute> = <value>
        for collection_name in collections:
            collection = schema.get_collection(collection_name)
            if not is_valid_collection(collection):
                return
            if not is_validate_where(query):
                return
            segment = query[5]
            attribute = query[6]
            operator = query[7]
            if not is_operator(operator):
                return
            value = query[8]
            results = get_resources_by_segment_attribute_value(collection, segment, attribute, operator, value)
            print_select(schema, query, results)
    elif len(query) == 10:
        # get <qualifier> from <collection_list> where <attribute> = <low> : <high>
        for collection_name in collections:
            collection = schema.get_collection(collection_name)
            if not is_valid_collection(collection):
                return
            if not is_validate_where(query):
                return
            attribute = query[5]
            low = query[7]
            rng = query[8]
            if not is_range_operator(rng):
                return
            high = query[9]
            if not is_valid_range(low, high):
                return
            results = get_resources_by_attribute_range(collection, attribute, float(low), float(high), False)
            print_select(schema, query, results)
    elif len(query) == 11 and query[6] != "with":
        # get <qualifier> from <collection_list> where <segment> <attribute> = <low> : <high>
        for collection_name in collections:
            collection = schema.get_collection(collection_name)
            if not is_valid_collection(collection):
                return
            if not is_validate_where(query):
                return
            segment = query[5]
            attribute = query[6]
            low = query[8]
            rng = query[9]
            if not is_range_operator(rng):
                return
            high = query[10]
            if not is_valid_range(low, high):
                return
            results = get_resources_by_segment_attribute_range(collection, segment, attribute, float(low),
                                                               float(high))
            print_select(schema, query, results)
    elif len(query) == 11 and query[6] == "with":
        # select <qualifier> from <collection_list> where <segment1> <segment2> with <attribute> <operator> <value>
        for collection_name in collections:
            collection = schema.get_collection(collection_name)
            if not is_valid_collection(collection):
                return
            if not is_validate_where(query):
                return
            segment1 = query[5]
            segment2 = query[7]
            attribute = query[8]
            operator = query[9]
            if not is_operator(operator):
                return
            value = query[10]
            results = get_resources_by_2segments_attribute_value(collection, segment1, segment2, attribute, operator,
                                                                 value)
            print_select(schema, query, results)
    elif len(query) == 13 and query[6] == "with":
        # select <qualifier> from <collection_list> where <segment1> with <segment2> <attribute> <operator> low : high
        for collection_name in collections:
            collection = schema.get_collection(collection_name)
            if not is_valid_collection(collection):
                return
            if not is_validate_where(query):
                return
            segment1 = query[5]
            segment2 = query[7]
            attribute = query[8]
            low = query[10]
            rng = query[11]
            if not is_range_operator(rng):
                return
            high = query[12]
            results = get_resources_by_2segments_attribute_range(collection, segment1, segment2, attribute,
                                                                 float(low), float(high))
            print_select(schema, query, results)
    else:
        print("Invalid command - check number of parameters")

#
#   Process a get command.
#
def get_resource_by_id(schema, query):
    temp_results = schema.get_collection("Result")
    if temp_results is None:
        print("Invalid Collection")
        return
    if len(query) != 4:
        print("Missing number of arguments")
        return
    collection = schema.get_collection(query[3])
    if collection is None:
        print("Invalid collection")
        return

    id = query[1]
    result = collection.get(id)
    temp_results.resources.append(result)
    print(result)
    return


def is_valid_insert_command(schema, command_line):
    if len(command_line) < 5:
        print("Invalid insert command: too few arguments")
        return False
    if command_line[3] != "into":
        print("Invalid insert command:", command_line[3], "use into keyword")
        return False
    if not collection_exists(schema, command_line[4]):
        print("Invalid insert command:", command_line[4], "collection does not exist")
        return False

    return True


#
# Process an Insert command.
# insert json|file <filename> into <collection>
#
def insert_resource(schema, command_line):
    if not is_valid_insert_command(schema, command_line):
        return
    # Create a resource
    collection_name = command_line[4]
    collection = schema.get_collection(collection_name)
    if collection is None:
        print("Invalid Collection")
        return None

    resource = Resource(collection_name)

    if command_line[1] == "json":
        resource.type = collection_name
        resource.data = command_line[2]
        collection.add_resource(resource)
        resource.save()
        print(resource.uuid)
    elif command_line[1] == "file" or len(command_line[1]) > 0:
        if not resource.load_file(command_line[2], ""):
            print("File not Found")
            return None
        collection.add_resource(resource)
        resource.save()
        print(resource.uuid)
    else:
        print("Invalid insert command")
        return None


#
#   Bulk Load a file into a collection
#
def load(schema, command_line):
    if not is_valid_insert_command(schema, command_line):
        return
    n = int(command_line[1])
    for i in range(0, n):
        insert_resource(schema, command_line)


#
# Validate an update command.
#
def is_valid_update_command(schema, command_line):
    if len(command_line) != 8:
        print("Invalid update command: too few arguments")
        return False
    if command_line[4] != "where":
        print("Invalid update command: missing where keyword")
        return False
    if command_line[5] != "id":
        print("Invalid update command: id missing")
        return False
    if command_line[6] != "=":
        print("Invalid update command: = missing")
        return False
    if len(command_line[7]) < 36:
        print("Invalid update command: invalid uuid")
        return False
    return True


#
# Process an update command.
# update <collection> json <json> where id = <id>
# update <collection> file <filename> where id = <id>
#
def update_resource(schema, command_line):
    # TODO json must have no spaces
    if not is_valid_update_command(schema, command_line):
        return
    data = ""
    collection_name = command_line[1]
    if command_line[2] == "json":
        data = command_line[3]
    elif command_line[2] == "file":
        resource = Resource(collection_name)
        resource.load_file(command_line[3], "")
        data = resource.data

    id = command_line[7]
    collection = schema.get_collection(collection_name)
    if collection is None:
        print("Invalid Collection")
        return

    for resource in collection.resources:
        if str(resource.uuid) == str(id):
            resource.data = data
            resource.save()
            return
    print("Update command: Resource not found")
    return


def is_valid_copy_command(schema, command_line):
    if len(command_line) != 4:
        print("Invalid copy command: too few arguments")
        return False
    if command_line[2] != "to":
        print("Invalid copy command: use the to keyword")
        return False
    from_name = command_line[1]
    if not collection_exists(schema, from_name):
        print("Invalid copy command: from collection does not exist")
        return False
    return True


#
# Process a copy command:
# copy <source> to <destination>
#
def copy_collection(schema, command_line):
    if not is_valid_copy_command(schema, command_line):
        return
    from_name = command_line[1]
    to_name = command_line[3]

    if not collection_exists(schema, to_name):
        create_collection(schema, to_name)

    from_collection = schema.get_collection(from_name)
    to_collection = schema.get_collection(to_name)

    if to_collection is None or from_collection is None:
        print("Invalid Collection")
        return

    for resource in from_collection.resources:
        r = Resource(from_name)
        r.uuid = resource.uuid
        r.type = to_name
        r.data = resource.data
        r.state = resource.state
        to_collection.resources.append(r)
    to_collection.save()

#
# Reverse a collection's order.
#
def reverse_collection(schema, command_line):
    if len(command_line) < 2:
        print("Too few arguments - collection name missing")
        return
    collection_name = command_line[1]
    collection = schema.get_collection(collection_name)
    if collection is None:
        print("Invalid Collection")
        return

    collection.reverse()

#
# Randomise a collection's order.
#
def randomise_collection(schema, command_line):
    collection_name = command_line[1]
    collection = schema.get_collection(collection_name)
    if collection is None:
        print("Invalid Collection")
        return

    collection.randomise()

def display_help():
    print(HELP)


def display_info(schema):
    print(schema.name + ", " + schema.version + " by " + schema.author)
    for collection in schema.collections:
        print(collection.name + ": " + str(len(collection.resources)) + " entries")


# Create a new collection
def create_collection(schema, command_line):
    # Test if the collection exists
    collection_name = command_line[1]
    if collection_exists(schema, collection_name):
        print(collection_name, "Collection exists")
        return False

    # Make the collection in file system and schema
    try:
        path = os.path.join(Schema.ROOT, collection_name)
        os.makedirs(path)
        collection = Collection(collection_name)
        schema.collections.append(collection)
        print("Collection", collection_name, "created")
        return True
    except IOError:
        print("Cannot create collection")
        return False


def collection_exists(schema, collection_name):
    for collection in schema.collections:
        if collection_name == collection.name:
            return True
    return False

    #
    # Create a new collection.
    pass


def create_results_collection(schema):
    try:
        collection_name = "Result"
        path = os.path.join(Schema.ROOT, collection_name)
        os.makedirs(path)
        collection = Collection(collection_name)
        schema.collections.append(collection)
    except IOError:
        pass

#
# Display the results temporary table.
#
def display_results(schema):
    history = schema.get_collection("Result")
    if history is not None:
        for h in history.resources:
            print(h)
    else:
        print("Invalid Collection, create Result collection")

#
# Clear the result collection.
#
def clear_results(schema):
    results = schema.get_collection("Result")
    if results is None:
        create_results_collection(schema)
        return
    results.clear()