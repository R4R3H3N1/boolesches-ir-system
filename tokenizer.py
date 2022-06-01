import re, os, sys
from indexer import Index

def get_token_from_line(line):
    return [x.lower() for x in re.split("[ |\"|\?|,|!|.|&|\n|;|:|...|-|\\\|/|(|)|\[|\]]", line) if x != '']

def tokenize_documents(documents: list[str]):
    """    tokens = []
    for i in range(len(documents)):
        with open(documents[i]) as doc:
            lines = doc.readlines()"""

    for line in documents:
        tmp = re.split(r'\$\$\$', line)
        if len(tmp) != 2: # warum taucht leerstring auf?
            #print(tmp)
            continue
        docID, text = tmp[0], tmp[1]
        new_tokens = get_token_from_line(text)
        yield docID, new_tokens
                #for new_token in new_tokens:
                    #tokens.append(new_token)

    #return tokens




def parse_doc_dump():
    # nfcorpus/raw/doc_dump.txt
    # Format pro Zeile ID \t URL \t TITLE \t ABSTRACT \r\n
    # ID und ABSTRACT extrahieren
    # speichern unter ID.txt

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
        abstract = re.sub(r'^Abstract', '', abstract).strip()

        newDocument += (ID + '$$$' + abstract + '\n')

    with open('ID.txt', 'w', encoding='utf8') as f:
        f.write(newDocument)

if __name__ == '__main__':
    # creates ID.txt
    #parse_doc_dump()

    i = Index('ID.txt')
    i.to_json()