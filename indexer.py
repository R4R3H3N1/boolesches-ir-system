from __future__ import annotations

import time

from tokenizer import tokenize_documents
import json
from typing import Type, List, Set
import configuration
import levenshtein
from jaccard_index import jaccard_index


# =========================================================================== #
class Index:
    __slots__ = ('dictionary', 'termClassMapping', 'documentIDs', 'kgramMap')

    def __init__(self, filename: str):
        # dict[TermIndex, Postinglist]
        self.dictionary = {}
        self.termClassMapping = {}
        self.kgramMap = {}
        self.documentIDs = set()
        # TODO Sortierungsschritte (notwendig?)
        if not configuration.READ_DICTIONARY_FROM_JSON:
            print("Started creating index")
            start = time.time()
            self.invoke_toknizer(filename)
            print(f"Creating index took {time.time() - start} seconds.")
            if configuration.KGRAM_INDEX_ENABLED:
                print("Started creating kgram-index")
                start = time.time()
                self.create_kgram_index()
                print(f"Creating kgram-index took {time.time() - start} seconds.")
        else:
            print("Started creating index from JSON file")
            start = time.time()
            self.from_json()
            print(f"Creating index took {time.time() - start} seconds.")
            if configuration.KGRAM_INDEX_ENABLED:
                print("Started creating kgram-index")
                start = time.time()
                self.create_kgram_index()
                print(f"Creating kgram-index took {time.time() - start} seconds.")

    # --------------------------------------------------------------------------- #
    def invoke_toknizer(self, filename: str) -> None:
        # TODO skip-pointer
        # TODO nur Differenz der DocIDs speichern

        try:
            with open(filename, 'r', encoding='utf8') as f:
                file = f.read()
                docs = file.split('\n')
        except FileNotFoundError:
            print(f'ERROR: file {filename} not found')
            return

        for docID, tokens in tokenize_documents(docs):
            positionCounter = 1
            self.documentIDs.add(docID)
            for token in tokens:
                try:
                    ti = self.termClassMapping[token]
                except KeyError:
                    ti = TermIndex(token)
                    self.termClassMapping[token] = ti

                try:
                    self.dictionary[ti].append(docID, positionCounter)
                    ti.occurence += 1
                except KeyError:
                    self.dictionary[ti] = Postinglist(docID, positionCounter)

                positionCounter += 1

        for key, val in self.dictionary.items():
            val.final_sort()

    # --------------------------------------------------------------------------- #
    def create_kgram_index(self):
        for termindex in self.dictionary.keys():
            kgrams = self.kgrams(termindex.term, k=configuration.K)
            for kgram in kgrams:
                try:
                    if termindex not in self.kgramMap[kgram]:
                        self.kgramMap[kgram].append(termindex)
                except KeyError:
                    self.kgramMap[kgram] = [termindex]

    def kgrams(self, term: str, k: int) -> List[str]:
        kgrams = []
        for i in range(len(term) - k + 1):
            kgrams.append(term[i:i + k])
        return kgrams

    # --------------------------------------------------------------------------- #
    def find_alternative_docids(self, term: str) -> Postinglist:
        alternative_terms = self.find_term_alternatives(term.strip())
        print(f"Spell checker found the following alternative terms: {alternative_terms}.")
        result = Postinglist()

        for alternative_term in alternative_terms:
            posting_list = self.dictionary[self.termClassMapping[alternative_term]]
            for doc_id in posting_list.plist:
                result.append(doc_id, posting_list.positions[doc_id])

        result.final_sort()
        return result

    def find_term_alternatives(self, term: str) -> List[str]:
        term_kgrams = self.kgrams(term, k=configuration.K)
        threshold = int(.7 * len(term_kgrams))
        candidate_terms = []
        for kgram in term_kgrams:
            try:
                termindexList = self.kgramMap[kgram]
            except KeyError:
                continue
            for termIndex in termindexList:
                candidate_terms.append(termIndex.term)

        # Filter with Jaccard Index
        candidates_after_jaccard = []
        for candidate_term in candidate_terms:
            candidate_kgrams = self.kgrams(candidate_term, configuration.K)
            if jaccard_index(term_kgrams, candidate_kgrams) >= configuration.J:
                candidates_after_jaccard.append(candidate_term)

        # Filter candidates again after Levenshtein Distance
        candidates_after_levenshtein = []
        for candidate_term in candidates_after_jaccard:
            if levenshtein.levenshtein_distance(term, candidate_term) <= configuration.MAX_LEVENSHTEIN_DISTANCE:
                candidates_after_levenshtein.append(candidate_term)

        return candidates_after_levenshtein

    # --------------------------------------------------------------------------- #
    def to_json(self) -> None:
        obj = {}
        for key, val in self.dictionary.items():
            obj.update({key.term: {'key_occurence':key.occurence,
                                   'postinglist':val.plist,
                                   'positions':val.positions,
                                   'counts':val.counts}
                        })
        with open(configuration.JSON_FILE, 'w') as f:
            json.dump(obj, f)

    # --------------------------------------------------------------------------- #
    def from_json(self) -> None:
        """
        with open('index.json', 'r', encoding='utf8') as f:
            readIndex = json.load(f)
        a = 1
        for term, indexinfo in readIndex.items():
            pass
        """
        pass

    """
    # --------------------------------------------------------------------------- #
    def merge(self, str1: str, str2: str = None, operator: str = 'and') -> List[int]:
        # TODO mehrere Postinglisten
        Postinglist1 = self.dictionary[self.termClassMapping[str1]]
        if str2:
            Postinglist2 = self.dictionary[self.termClassMapping[str2]]
        # TODO handling wenn nur ein String, aber Operation mit 2 Listen

        if operator in ['and', 'AND']:
            return self.merge_AND(Postinglist1.plist, Postinglist2.plist)

        elif operator in ['or', 'OR']:
            return self.merge_OR(Postinglist1.plist, Postinglist2.plist)

        elif operator in ['not', 'NOT']:
            return self.merge_NOT(Postinglist1.plist, docIDSet=self.documentIDs)

        elif operator in ['and not', 'AND NOT']:
            return self.merge_ANDNOT(Postinglist1.plist, Postinglist2.plist)
    """

    # --------------------------------------------------------------------------- #
    # TODO term3 implemntieren
    def phrase_query(self, posting_list1: Postinglist, posting_list2: Postinglist,
                     posting_list3: Postinglist = None) -> Postinglist:

        result = Postinglist()

        if posting_list3 is None:
            candidates = self.merge_AND(posting_list1, posting_list2)

            for docID in candidates:
                for pos1 in posting_list1.positions[docID]:
                    for pos2 in posting_list2.positions[docID]:
                        if pos1 == pos2 - 1 and docID not in result:
                            result.append(docID, -1)
        else:
            candidates = self.merge_AND(self.merge_AND(posting_list1, posting_list2), posting_list3)

            for docID in candidates:
                for pos1 in posting_list1.positions[docID]:
                    for pos2 in posting_list2.positions[docID]:
                        for pos3 in posting_list3.positions[docID]:
                            if pos1 == pos2 - 1 and pos2 == pos3 - 1 and docID not in result:
                                result.append(docID, -1)

        return result

    # --------------------------------------------------------------------------- #
    def proximity_query(self, posting_list1: Postinglist, posting_list2: Postinglist, k: int = 1) -> Postinglist:

        candidates = self.merge_AND(posting_list1, posting_list2)
        result = Postinglist()

        for docID in candidates:
            for pos1 in posting_list1.positions[docID]:
                for pos2 in posting_list2.positions[docID]:
                    if abs(pos1-pos2) <= k and docID not in result:
                        result.append(docID, -1)

        return result

    # --------------------------------------------------------------------------- #
    @staticmethod
    def merge_AND(posting_list1: Postinglist, posting_list2: Postinglist) -> Postinglist:
        i, j = 0, 0
        result = Postinglist()

        while i < len(posting_list1.plist) and j < len(posting_list2.plist):
            if posting_list1.plist[i] == posting_list2.plist[j]:
                result.append_list_pos(posting_list1.plist[i], posting_list1.positions[posting_list1.plist[i]] +
                              posting_list2.positions[posting_list2.plist[j]])
                i += 1
                j += 1
            else:
                if posting_list1.plist[i] < posting_list2.plist[j]:
                    i += 1
                else:
                    j += 1
        return result

    # --------------------------------------------------------------------------- #
    @staticmethod
    def merge_OR(posting_list1: Postinglist, posting_list2: Postinglist) -> Postinglist:
        result = Postinglist()
        i, j = 0, 0
        while i < len(posting_list1.plist) and j < len(posting_list2.plist):
            if posting_list1.plist[i] == posting_list2.plist[j]:
                result.append_list_pos(posting_list1.plist[i], posting_list1.positions[posting_list1.plist[i]] +
                              posting_list2.positions[posting_list2.plist[j]])
                i += 1
                j += 1
            elif posting_list1.plist[i] < posting_list2.plist[j]:
                result.append_list_pos(posting_list1.plist[i], posting_list1.positions[posting_list1.plist[i]])
                i += 1
            elif posting_list1.plist[i] > posting_list2.plist[j]:
                result.append_list_pos(posting_list2.plist[j], posting_list2.positions[posting_list2.plist[j]])
                j += 1

        if i != len(posting_list1.plist):
            for x in range(i, len(posting_list1.plist)):
                result.append_list_pos(posting_list1.plist[x], posting_list1.positions[posting_list1.plist[x]])
        if j != len(posting_list2.plist):
            for x in range(j, len(posting_list2.plist)):
                result.append_list_pos(posting_list2.plist[x], posting_list2.positions[posting_list2.plist[x]])

        return result

    # --------------------------------------------------------------------------- #
    @staticmethod
    def merge_NOT(posting_list1: Postinglist, docIDSet: Set[int]) -> Postinglist:
        result = Postinglist()

        pl1set = set(posting_list1.plist)
        for docID in docIDSet:
            if docID in pl1set:
                pass
            else:
                result.append(str(docID), -1)
        return result

    # --------------------------------------------------------------------------- #
    @staticmethod
    def merge_ANDNOT(posting_list1: Postinglist, posting_list2: Postinglist) -> Postinglist:
        result = Postinglist()
        i = 0
        j = 0
        while i < len(posting_list1.plist) and j < len(posting_list2.plist):
            if posting_list1.plist[i] == posting_list2.plist[j]:
                i += 1
                j += 1
            elif posting_list1.plist[i] < posting_list2.plist[j]:
                result.append_list_pos(posting_list1.plist[i], posting_list1.positions[posting_list1.plist[i]])
                i += 1
            elif posting_list1.plist[i] > posting_list2.plist[j]:
                j += 1

        if i != len(posting_list1.plist):
            for x in range(i, len(posting_list1.plist)):
                result.append_list_pos(posting_list1.plist[x], posting_list1.positions[posting_list1.plist[x]])

        return result


# =========================================================================== #
class TermIndex:
    __slots__ = ('term', 'occurence')

    def __init__(self, term: str):
        self.term = term
        self.occurence = 1

    def __hash__(self):
        return hash(self.term)


# =========================================================================== #
class Postinglist:
    __slots__ = ('plist', 'seenDocIDs', 'positions', 'counts')

    def __init__(self, docID: int = None, position: int = None):
        # TODO array.array, numpy array oder liste?
        self.plist = []   # List of sorted DocIDs

        self.positions = {}  # map docID:positions within docID
        self.counts = {} # map docID:#occurence within docID
        # TODO counts notwendig?
        # TODO ein Objekt für alle drei?

        self.seenDocIDs = set()
        if docID:
            self.append(docID, position)

    def __len__(self):
        return len(self.plist)

    def __getitem__(self, idx):
        return self.plist[idx]

    def append(self, docID: str, position: int) -> None:
        # TODO wenn in verschiedenen Objekten, dann in Funktionen aufspalten
        try:
            self.positions[docID].append(position)
        except KeyError:
            self.positions[docID] = [position]

        try:
            self.counts[docID] += 1
        except KeyError:
            self.counts[docID] = 1

        if docID in self.seenDocIDs:
            pass
        else:
            self.plist.append(docID)
            self.seenDocIDs.add(docID)

    def append_list_pos(self, docID: str, positions: List[int]) -> None:
        # TODO wenn in verschiedenen Objekten, dann in Funktionen aufspalten
        try:
            self.positions[docID] += positions
        except KeyError:
            self.positions[docID] = positions

        try:
            self.counts[docID] += len(positions)
        except KeyError:
            self.counts[docID] = len(positions)

        if docID in self.seenDocIDs:
            pass
        else:
            self.plist.append(docID)
            self.seenDocIDs.add(docID)

    def final_sort(self) -> None:
        self.plist = sorted(self.plist)
        #, key=lambda x: int(x.split('-')[1]))


