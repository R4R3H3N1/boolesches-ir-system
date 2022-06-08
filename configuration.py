IO_FOLDER = "io"

ID_FILE = "ID.txt"

JSON_FILE = "index.json"

PARSE_DOC_DUMP = True

WRITE_DICTIONARY_INTO_JSON = False

READ_DICTIONARY_FROM_JSON = False

ABSTRACT_BEGINNINGS = ["Abstract", "Preface", "Summary", "Short", "Synopsis", "Excerpt"]

QUERY_EXAMPLES = ["blood", "blood AND pressure", "blood AND NOT pressure", "blood OR pressure AND cardiovascular",
                  "\"blood pressure\"", "diet \\10 health", "diet \\10 health AND \"red wine\""]
KGRAM_INDEX_ENABLED = True
# Trigger for Spell checking
R = 3
# K for k gram index used in spell checking
K = 3
# Threshold for Jaccard Index value between 0.0 - 1.0
J = 0.2
# Max levenshtein distance for correction term
MAX_LEVENSHTEIN_DISTANCE = 2
# INSIDE THE SPELL CHECKER GET EITHER ONLY ONE REPLACEMENT TERM OR MERGE IDs AND POSITIONS OF ALL POSSIBLE TERMS
ONLY_ONE_REPLACEMENT_TERM = True
# Activate Heuristic to Merge smallest PostingLists first in AND
ACTIVATE_SMALL_POSTINGLISTS_FIRST_HEURISTIC = True

