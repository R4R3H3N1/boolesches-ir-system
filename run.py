from query_processing import *
from tokenizer import *


# --------------------------------------------------------------------------- #
def input_query(indexer):
    print("In the prompt below you can enter a query in KNF.")
    print("The result will be a list of document IDs which fulfill the query.")
    print("Queries including the OR operator should NOT be written in brackets.")
    print("You can choose from the following operators (capslock important):")
    print("AND, OR, NOT, \\k, \"term1 term2 (term3)\".")
    print("Currently not working are queries inside the proximity - or phrase query operators (i.e: \"(term1 \\10 term2) term3\".")
    print("Enter exit() to leave the input query.")
    print("You can also choose from the following " + str(len(configuration.QUERY_EXAMPLES)) + " examples:")

    query = QueryProcessing(indexer)
    for j in range(len(configuration.QUERY_EXAMPLES)):
        print(str(j) + ": " + configuration.QUERY_EXAMPLES[j])
    while True:
        query_string = input("Enter your Query in KNF: ")
        for j in range(len(configuration.QUERY_EXAMPLES)):
            if query_string == str(j):
                query_string = configuration.QUERY_EXAMPLES[j]
        if query_string == "exit()":
            break
        print("--------------------------------------------------")
        print("Starting Query with following KNF: " + query_string)
        start = time.time()
        result = query.execute_query(query_string)
        print(f"Result: {result.plist}")
        print(f"Query execution took {time.time() - start} seconds")
        print("--------------------------------------------------")


# --------------------------------------------------------------------------- #
if __name__ == '__main__':

    # creates ID.txt including all doc ids and abstracts
    if configuration.PARSE_DOC_DUMP:
        parse_doc_dump()

    i = indexer.Index(configuration.ID_FILE)

    # Writes dictionary into json file such that it can be loaded next time
    if configuration.WRITE_DICTIONARY_INTO_JSON:
        i.to_json()

    input_query(i)

    # TODO Optimierungen, z.B. mit seltenstem Term beginnen
