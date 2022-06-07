import configuration
from indexer import *
from tokenizer import *
from query_processing import *

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
