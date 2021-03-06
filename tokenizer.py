import os
import re
from typing import List, Generator, Tuple

import configuration


# --------------------------------------------------------------------------- #
def get_token_from_line(line: str) -> List[str]:

    line = line.lower()

    for character in configuration.TERM_SPLIT_CHARACTERS:
        line = line.replace(character, " ")

    #if line[len(line) - 1] == ".":
    if line.endswith('.'):
        line = line[:-1]

    return [x.strip() for x in re.split(" ", line) if x not in configuration.STOP_WORDS]


# --------------------------------------------------------------------------- #
def exclude_abstract_beginnings(abstract: str) -> str:
    """
    remove terms like preface, summary, etc. from document abstarct
    """
    for beginning in configuration.ABSTRACT_BEGINNINGS:
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
    """
    transform doc_dump.txt into pairs of ID and text
    """
    docdumpPath = configuration.DATA_LOCATION
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

    try:
        os.mkdir(os.path.join(os.getcwd(), configuration.IO_FOLDER))
    except Exception:
        pass

    with open(os.path.join(os.getcwd(), configuration.IO_FOLDER, configuration.ID_FILE), 'w', encoding='utf8') as f:
        f.write(newDocument)


