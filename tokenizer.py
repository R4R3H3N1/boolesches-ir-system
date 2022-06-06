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
if __name__ == '__main__':

    # creates ID.txt including all doc ids and abstracts
    if PARSE_DOC_DUMP:
        parse_doc_dump()

    i = indexer.Index(ID_FILE)

    # Writes dictionary into json file such that it can be loaded next time
    if WRITE_DICTIONARY_INTO_JSON:
        i.to_json()

    query = query_processing.QueryProcessing(i)

    blood_query = query.execute_query("blood")
    pressure_query = query.execute_query("pressure")
    blood_and_pressure_query = query.execute_query("blood AND pressure")
    print(blood_query)
    print(pressure_query)
    print(blood_and_pressure_query)
    is_correct = True
    for docId in blood_and_pressure_query:
        if  not docId in blood_query or not docId in pressure_query:
            is_correct = False
    print(is_correct)

    # TODO Optimierungen, z.B. mit seltenstem Term beginnen

    #print(i.phrase_query('capsaicin', 'contained'))

    #print(i.proximity_query('useful', 'kiwifruit', k=4))

    #print(i.merge('acrylamide-containing', 'background', operator='and'))
    #print(i.merge('acrylamide-containing', 'placenta', operator='or'))
    #print(i.merge('and', operator='not'))

