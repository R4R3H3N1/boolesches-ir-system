import re, os, sys
import indexer
from typing import List, Generator, Tuple

# --------------------------------------------------------------------------- #
def get_token_from_line(line: str) -> List[str]:
    return [x.lower() for x in re.split("[ |\"|\?|,|!|.|&|\n|;|:|...|-|\\\|/|(|)|\[|\]]", line) if x != '']


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
    # TODO case-folding and further preprocessing

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
        abstract = re.sub(r'^Abstract', '', abstract, re.IGNORECASE).strip() #preface

        newDocument += (ID + '$$$' + abstract + '\n')
        # TODO allgemeiner, nicht von $$$ abhängig

    with open('ID.txt', 'w', encoding='utf8') as f:
        f.write(newDocument)


# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    # creates ID.txt
    #parse_doc_dump()

    i = indexer.Index('ID.txt')
    #i.to_json()

    print(i.merge('acrylamide-containing', 'background', operator='and'))

    print(i.merge('acrylamide-containing', 'placenta', operator='or'))

    print(i.merge('and', operator='not'))

