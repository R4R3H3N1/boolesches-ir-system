import os

DATA_LOCATION = os.path.join(os.getcwd(), "nfcorpus", "raw", "doc_dump.txt")

IO_FOLDER = "io"

ID_FILE = "ID.txt"

JSON_FILE = "index.json"

PARSE_DOC_DUMP = True

WRITE_DICTIONARY_INTO_JSON = False

# Does not work currently see comment in to_json function in indexer.py
READ_DICTIONARY_FROM_JSON = False

STOP_WORDS = [" ", "", "abstract", "excerpt", "preface", "summary", "short", "preface", "ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with ", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", " your ", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"]
TERM_SPLIT_CHARACTERS = ["\" ", " \"", "?", ", ", "!", ".\n", ". ", "&", "\n", ";", ":", "...", " - ", "\\", "/", "(", ")", "[", "]"]

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
ONLY_ONE_REPLACEMENT_TERM = False
# Activate Heuristic to Merge smallest PostingLists first in AND
ACTIVATE_SMALL_POSTINGLISTS_FIRST_HEURISTIC = True
# Activate Skip pointer for faster AND and AND NOT merging
ACTIVATE_SKIP_POINTER = True

