import re, os, sys
import indexer
from typing import List, Generator, Tuple
from configuration import *
import query_processing


# --------------------------------------------------------------------------- #
def get_token_from_line(line: str) -> List[str]:
    return [x.lower() for x in re.split("[ |\"|\?|,|!|.|&|\n|;|:|...|-|\\\|/|(|)|\[|\]]", line) if x != '']


# --------------------------------------------------------------------------- #
def exclude_abstract_beginnings(abstract) -> str:
    for beginning in ABSTRACT_BEGINNINGS:
        abstract = re.sub(r'^' + beginning, '', abstract, re.IGNORECASE).strip()
    return abstract


# --------------------------------------------------------------------------- #
def tokenize_documents(documents: List[str]) -> Generator[Tuple[str, List[str]], None, None]:
    """
    :param documents: list of documents
    :return: generator - docID, tokens in order of apperance
    """
    for line in documents:
        tmp = re.split(r'\$\$\$', line)
        if len(tmp) != 2: # warum taucht leerstring auf?
            continue
        docID, text = tmp[0], tmp[1]
        new_tokens = get_token_from_line(text)

        yield int(docID), new_tokens


# --------------------------------------------------------------------------- #
def parse_doc_dump() -> None:
    # TODO further preprocessing?

    docdumpPath = os.path.join(os.getcwd(), 'nfcorpus', 'raw', 'doc_dump.txt')
    newDocument = ''
    try:
        with open(docdumpPath, 'r', encoding='utf8') as f:
            file = f.read()
            file = file.split('\n')
    except FileNotFoundError:
        print(f'error opening file {docdumpPath}')
        return

    for line in file:
        docContent = re.split(r'\t', line)
        ID, abstract = docContent[0], docContent[3]

        ID = ID.replace('MED-', '')
        abstract = exclude_abstract_beginnings(abstract)

        newDocument += (ID + '$$$' + abstract + '\n')
        # TODO allgemeiner, nicht von $$$ abhängig
        # TODO strings wie $$$BACKGROUND oder $$$preface auch entfernen (?)

    with open('ID.txt', 'w', encoding='utf8') as f:
        f.write(newDocument)


# --------------------------------------------------------------------------- #
def input_query():
    print("In the following one can enter a query in KNF.")
    print("The result will be a list of document IDs which fulfill the query.")
    print("Queries including the OR operator should not be written in brackets.")
    print("One can choose from the following operators (capslock important):")
    print("AND, OR, NOT, \\k, \"term1 term2 (term3)\".")
    print("Currently not working are queries inside the proximity - or phrase query operators (i.e: \"(term1 \\10 term2) term3\".")
    print("Enter exit() to leave the input query.")
    print("One can also choose from the following " + str(len(QUERY_EXAMPLES)) + " examples:")
    for j in range(len(QUERY_EXAMPLES)):
        print(str(j) + ": " + QUERY_EXAMPLES[j])
    while True:
        query_string = input("Enter your Query in KNF: ")
        for j in range(len(QUERY_EXAMPLES)):
            if query_string == str(j):
                query_string = QUERY_EXAMPLES[j]
        if query_string == "exit()":
            break
        print("Starting Query with following KNF: " + query_string)
        result = query.execute_query(query_string)
        print("Result:")
        print(result)


# --------------------------------------------------------------------------- #
if __name__ == '__main__':

    # creates ID.txt including all doc ids and abstracts
    if PARSE_DOC_DUMP:
        parse_doc_dump()

    i = indexer.Index(ID_FILE)

    # Writes dictionary into json file such that it can be loaded next time
    if WRITE_DICTIONARY_INTO_JSON:
        i.to_json()

    query = query_processing.QueryProcessing(i)

    input_query()

    # TODO Optimierungen, z.B. mit seltenstem Term beginnen

    #print(i.phrase_query('capsaicin', 'contained'))

    #print(i.proximity_query('useful', 'kiwifruit', k=4))

    #print(i.merge('acrylamide-containing', 'background', operator='and'))
    #print(i.merge('acrylamide-containing', 'placenta', operator='or'))
    #print(i.merge('and', operator='not'))

