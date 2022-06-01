# This will be the tokenizer
import re


def get_token_from_line(line):
    return [x.lower() for x in re.split(" |\"|\?|,|!|.|&", line) if x != '']


def tokenize_documents(documents):
    tokens = []
    for i in range(len(documents)):
        with open(documents[i]) as doc:
            lines = doc.readlines()
            for line in lines:
                new_tokens = get_token_from_line(line)
                for new_token in new_tokens:
                    tokens.append(new_token)
