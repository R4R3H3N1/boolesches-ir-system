import re, os


def get_token_from_line(line):
    return [x.lower() for x in re.split("[ |\"|\?|,|!|.|&|\n|;|:|...|-|\\\|/|(|)|\[|\]]", line) if x != '']


def tokenize_documents(documents):
    tokens = []
    for i in range(len(documents)):
        with open(documents[i]) as doc:
            lines = doc.readlines()
            for line in lines:
                new_tokens = get_token_from_line(line)
                for new_token in new_tokens:
                    tokens.append(new_token)

    return tokens

# nfcorpus/raw/doc_dump.txt
# Format pro Zeile ID \t URL \t TITLE \t ABSTRACT \r\n
    # ID und ABSTRACT extrahieren
    # speichern unter ID.txt


def parse_doc_dump():
    doc_dump_path = os.path.join(os.getcwd(), 'nfcorpus', 'raw', 'doc_dump.txt')
    newDocument = ''
    try:
        with open(doc_dump_path, 'r', encoding='utf8') as f:
            file = f.read()
            file = file.split('\n')
    except FileNotFoundError:
        print(f'error opening file {doc_dump_path}')
        return

    for line in file:
        docContent = re.split(r'\t', line)
        ID, abstract = docContent[0], docContent[3]
        abstract = re.sub(r'^Abstract', '', abstract)

        newDocument += (ID + ' ' + abstract + '\n')

    with open('ID.txt', 'w', encoding='utf8') as f:
        f.write(newDocument)

if __name__ == '__main__':
    #parse_doc_dump()
    pass