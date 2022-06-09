import os
import re
from typing import List, Generator, Tuple

import configuration


# --------------------------------------------------------------------------- #
def get_token_from_line(line: str) -> List[str]:
    return [x.lower() for x in re.split("[ |\"|\?|,|!|.|&|\n|;|:|...|-|\\\|/|(|)|\[|\]|\“]", line) if x != '']


# --------------------------------------------------------------------------- #
def exclude_abstract_beginnings(abstract: str) -> str:
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

    try:
        os.mkdir(os.path.join(os.getcwd(), configuration.IO_FOLDER))
    except Exception:
        pass

    with open(os.path.join(os.getcwd(), configuration.IO_FOLDER, configuration.ID_FILE), 'w', encoding='utf8') as f:
        f.write(newDocument)


