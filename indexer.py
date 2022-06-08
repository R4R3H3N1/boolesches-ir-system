from __future__ import annotations

import numpy as np

from tokenizer import tokenize_documents
import json
import time
import os
from typing import Type, List, Set

import configuration
from algorithms import jaccard_coefficient, levenshtein_distance


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
            print(f"Creating index took {round(time.time() - start, 3)} seconds.")
            if configuration.KGRAM_INDEX_ENABLED:
                print("Started creating kgram-index")
                start = time.time()
                self.create_kgram_index()
                print(f"Creating kgram-index took {round(time.time() - start, 3)} seconds.")
            if configuration.ACTIVATE_SKIP_POINTER:
                self.create_skip_pointer()
        else:
            print("Started creating index from JSON file")
            start = time.time()
            self.from_json()
            print(f"Creating index took {time.time() - start} seconds.")
            if configuration.KGRAM_INDEX_ENABLED:
                print("Started creating kgram-index")
                start = time.time()
                self.create_kgram_index()
                print(f"Creating kgram-index took {round(time.time() - start, 3)} seconds.")

    # --------------------------------------------------------------------------- #
    def invoke_toknizer(self, filename: str) -> None:
        # TODO skip-pointer (see below)
        # TODO nur Differenz der DocIDs speichern (Glaube nicht nötig da eh alles in den Hauptspeicher passt)

        try:
            with open(filename, 'r', encoding='utf8') as f:
                file = f.read()
                docs = file.split('\n')
        except FileNotFoundError:
            print(f'ERROR: file {filename} not found')
            return

        for docID, tokens in tokenize_documents(docs):
            positionCounter = 1
            int_doc_id = int(docID)
            self.documentIDs.add(int_doc_id)
            for token in tokens:
                try:
                    ti = self.termClassMapping[token]
                except KeyError:
                    ti = TermIndex(token)
                    self.termClassMapping[token] = ti

                try:
                    self.dictionary[ti].append(int_doc_id, positionCounter)
                    ti.occurence += 1
                except KeyError:
                    self.dictionary[ti] = Postinglist(int_doc_id, positionCounter)

                positionCounter += 1

        for key, val in self.dictionary.items():
            val.final_sort_postinglist()

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
    def create_skip_pointer(self):

        for termIndex in self.dictionary.keys():
            postinglist = self.dictionary[termIndex]
            skip_gap = int(np.sqrt(len(postinglist)))
            for i in range(0, len(postinglist) - int(len(postinglist) / skip_gap), int(len(postinglist) / skip_gap)):
                postinglist.skip_pointer[postinglist.plist[i]] = i + (int(len(postinglist) / skip_gap))
            if termIndex.term == "blood":
                print(postinglist.skip_pointer)

    # --------------------------------------------------------------------------- #
    def find_alternative_docids(self, term: str) -> Postinglist:
        # Finds all alternative terms based on kgrams, Jaccard Index and Levenshtein distance
        alternative_terms = self.find_term_alternatives(term.strip())
        print(f"Spell checker found the following alternative terms: {alternative_terms}.")
        result = Postinglist()

        # Merges Postinglists of all alternative terms
        if len(alternative_terms) > 1:
            for alternative_term in alternative_terms:
                posting_list = self.dictionary[self.termClassMapping[alternative_term]]
                for doc_id in posting_list.plist:
                    result.append(doc_id, posting_list.positions[doc_id])

            for doc_id in result.plist:
                result.positions[doc_id] = sorted(result.positions[doc_id])

            result.final_sort_postinglist()
        # Gets Postinglist of single alternative term
        elif len(alternative_terms) == 1:
            result = self.dictionary[self.termClassMapping[alternative_terms[0]]]

        return result

    # --------------------------------------------------------------------------- #
    def find_term_alternatives(self, term: str) -> List[str]:
        term_kgrams = self.kgrams(term, k=configuration.K)
        candidate_terms = set()
        for kgram in term_kgrams:
            try:
                termindexList = self.kgramMap[kgram]
            except KeyError:
                continue
            for termIndex in termindexList:
                if termIndex.term not in candidate_terms:
                    candidate_terms.add(termIndex.term)

        # Filter with Jaccard Index
        candidates_after_jaccard = []
        for candidate_term in candidate_terms:
            candidate_kgrams = self.kgrams(candidate_term, configuration.K)
            if jaccard_coefficient(term_kgrams, candidate_kgrams) >= configuration.J:
                candidates_after_jaccard.append(candidate_term)

        # Filter candidates again after Levenshtein Distance
        smallest_distance = 1000000
        distance_term_dict = {smallest_distance: []}
        for candidate_term in candidates_after_jaccard:
            levenshtein_distance_term = levenshtein_distance(term, candidate_term)
            if levenshtein_distance_term <= configuration.MAX_LEVENSHTEIN_DISTANCE:
                try:
                    distance_term_dict[levenshtein_distance_term].append(candidate_term)
                except KeyError:
                    distance_term_dict[levenshtein_distance_term] = [candidate_term]

                if levenshtein_distance_term < smallest_distance:
                    smallest_distance = levenshtein_distance_term

        # Only return the best replacement term if ONLY_ONE_REPLACEMENT_TERM is true
        # else return all replacements
        if configuration.ONLY_ONE_REPLACEMENT_TERM:
            candidates_after_levenshtein = distance_term_dict[smallest_distance]
            if len(candidates_after_levenshtein) > 1:
                candidates_after_levenshtein = [self.get_single_replacement_from_user(candidates_after_levenshtein)]
        else:
            candidates_after_levenshtein = []
            for distance, candidates in distance_term_dict.items():
                candidates_after_levenshtein += candidates

        return candidates_after_levenshtein

    def get_single_replacement_from_user(self, candidates):
        print("Spell checker found the following possible replacements please choose one of them: ")
        for i in range(len(candidates)):
            print(f"{i} {candidates[i]}")
        replacement_id = input("Enter the number of the wanted replacement: ")
        try:
            replacement_id = int(replacement_id)
        except ValueError:
            self.get_single_replacement_from_user(candidates)
        if replacement_id not in range(len(candidates)):
            self.get_single_replacement_from_user()

        return candidates[replacement_id]

    # --------------------------------------------------------------------------- #
    def to_json(self) -> None:
        obj = {}
        for key, val in self.dictionary.items():
            obj.update({key.term: {'key_occurence': key.occurence,
                                   'postinglist': val.plist,
                                   'positions': val.positions,
                                   'counts': val.counts}
                        })
        with open(os.path.join(os.getcwd(), configuration.IO_FOLDER, configuration.JSON_FILE), "w") as f:
            json.dump(obj, f)

    # --------------------------------------------------------------------------- #
    def from_json(self) -> None:

        # TODO does not work as JSON converts all keys into strings and we have int keys, exception occurs with
        #  example #1
        with open(os.path.join(os.getcwd(), configuration.IO_FOLDER, configuration.JSON_FILE), 'r', encoding='utf8') as f:
            readIndex = json.load(f)
        a = 1
        for term, indexinfo in readIndex.items():
            ti = TermIndex(term)
            ti.occurence = int(indexinfo["key_occurence"])
            self.termClassMapping[term] = ti
            posting_list = Postinglist()
            posting_list.plist = list(indexinfo["postinglist"])
            posting_list.positions = dict(indexinfo["positions"])
            posting_list.counts = dict(indexinfo["counts"])
            posting_list.seenDocIDs = list(indexinfo["postinglist"])
            self.dictionary[ti] = posting_list

    # --------------------------------------------------------------------------- #
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
                    if configuration.ACTIVATE_SKIP_POINTER:
                        try:
                            if posting_list1.plist[posting_list1.skip_pointer[posting_list1.plist[i]]] \
                                    <= posting_list2.plist[j]:
                                i = posting_list1.skip_pointer[posting_list1.plist[i]]
                            else:
                                i += 1
                        except KeyError:
                            i += 1
                    else:
                        i += 1
                else:
                    if configuration.ACTIVATE_SKIP_POINTER:
                        try:
                            if posting_list2.plist[posting_list2.skip_pointer[posting_list2.plist[j]]] \
                                    <= posting_list1.plist[i]:
                                j = posting_list2.skip_pointer[posting_list2.plist[j]]
                            else:
                                j += 1
                        except KeyError:
                            j += 1
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
                # TODO: why str() ?
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
                if configuration.ACTIVATE_SKIP_POINTER:
                    try:
                        if posting_list2.plist[posting_list2.skip_pointer[posting_list2.plist[j]]] \
                                <= posting_list1.plist[i]:
                            j = posting_list2.skip_pointer[posting_list2.plist[j]]
                        else:
                            j += 1
                    except KeyError:
                        j += 1
                else:
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
    __slots__ = ('plist', 'seenDocIDs', 'positions', 'skip_pointer',  'counts')

    def __init__(self, docID: int = None, position: int = None):
        # TODO array.array, numpy array oder liste?
        self.plist = []   # List of sorted DocIDs
        self.positions = {}  # map docID:positions within docID
        self.skip_pointer = {}  # map docID: skip_pointer position
        self.counts = {}  # map docID:#occurence within docID
        # TODO counts notwendig?
        # TODO ein Objekt für alle drei?

        self.seenDocIDs = set()
        if docID:
            self.append(docID, position)

    def __len__(self):
        return len(self.plist)

    def __getitem__(self, idx):
        return self.plist[idx]

    # --------------------------------------------------------------------------- #
    def append(self, docID: str, position: int | List[int]) -> None:
        #TODO keep this implementataion and delete function below, or delete list-part of this function
            #TODO is list-part deleted, use append_list_pos() in find_alternative_docids()
        if isinstance(position, list):
            try:
                [self.positions[docID].append(pos) for pos in position]
            except KeyError:
                self.positions[docID] = position
        else:
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

    def final_sort_postinglist(self) -> None:
        self.plist = sorted(self.plist)
