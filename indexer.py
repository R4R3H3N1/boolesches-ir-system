from tokenizer import tokenize_documents
import json
from typing import Type, List, Set

# =========================================================================== #
class Index:
    __slots__ = ('dictionary', 'termClassMapping', 'documentIDs')

    def __init__(self, filename: str):
        # dict[TermIndex, Postinglist]
        self.dictionary = {}
        self.termClassMapping = {}
        self.documentIDs = set()
        # sort term, dann sort docid
        # sortieren term überspringen, da kein unterschied in dict?

        self.invoke_toknizer(filename)

    # --------------------------------------------------------------------------- #
    def invoke_toknizer(self, filename: str) -> None:
        try:
            with open(filename, 'r', encoding='utf8') as f:
                file = f.read()
                docs = file.split('\n')
        except FileNotFoundError:
            print(f'error opening file {filename}')
            return


        for docID, tokens in tokenize_documents(docs):
            self.documentIDs.add(docID)
            for token in tokens:
                try:
                    ti = self.termClassMapping[token]
                except KeyError:
                    ti = TermIndex(token)
                    self.termClassMapping[token] = ti

                try:
                    self.dictionary[ti].append(docID)
                    ti.occurence += 1
                except KeyError:
                    self.dictionary[ti] = Postinglist(docID)

        for key, val in self.dictionary.items():
            val.final_sort()

    # --------------------------------------------------------------------------- #
    def to_json(self) -> None:
        obj = {}
        for key, val in self.dictionary.items():
            obj.update({key.term:(key.occurence, val.plist)})
        with open('index.json', 'w') as f:
            json.dump(obj, f)

    # --------------------------------------------------------------------------- #
    def from_json(self, filename: str) -> None:
        pass

    # --------------------------------------------------------------------------- #
    def merge(self, str1: str, str2: str = None, operator: str = 'and') -> List[int]:
        # //TODO mehrere Postinglisten
        Postinglist1 = self.dictionary[self.termClassMapping[str1]]
        if str2:
            Postinglist2 = self.dictionary[self.termClassMapping[str2]]
        #// TODO handling wenn nur ein String, aber Operation mit 2 Listen

        if operator in ['and', 'AND']:
            return self.merge_AND(Postinglist1.plist, Postinglist2.plist)

        elif operator in ['or', 'OR']:
            return self.merge_OR(Postinglist1.plist, Postinglist2.plist)

        elif operator in ['not', 'NOT']:
            return self.merge_NOT(Postinglist1.plist, docIDSet=self.documentIDs)

        elif operator in ['and not', 'AND NOT']:
            return self.merge_ANDNOT(Postinglist1.plist, Postinglist2.plist)


    # --------------------------------------------------------------------------- #
    @classmethod
    def merge_AND(Index, Postinglist1: List[int], Postinglist2: List[int]) -> List[int]:
        i, j = 0, 0
        result = []

        while i < len(Postinglist1) and j < len(Postinglist2):
            if Postinglist1[i] == Postinglist2[j]:
                result.append(Postinglist1[i])
                i += 1
                j += 1
            else:
                if Postinglist1[i] < Postinglist2[j]:
                    i += 1
                else:
                    j += 1
        return result

    # --------------------------------------------------------------------------- #
    @classmethod
    def merge_OR(Index, Postinglist1: List[int], Postinglist2: List[int]) -> List[int]:
        result = []
        i,j = 0,0
        while i < len(Postinglist1) and j < len(Postinglist2):
            if Postinglist1[i] == Postinglist2[j]:
                result.append(Postinglist1[i])
                i += 1
                j += 1
            elif Postinglist1[i] < Postinglist2[j]:
                result.append(Postinglist1[i])
                i += 1
            elif Postinglist1[i] > Postinglist2[j]:
                result.append(Postinglist2[j])
                j += 1

        if i != len(Postinglist1):
            for x in range(i, len(Postinglist1)):
                result.append(Postinglist1[x])
        if j != len(Postinglist2):
            for x in range(j, len(Postinglist2)):
                result.append(Postinglist2[x])

        return result

    # --------------------------------------------------------------------------- #
    @classmethod
    def merge_NOT(Index, Postinglist1: List[int], docIDSet: Set[int] = None) -> List[int]:
        result = []

        pl1set = set(Postinglist1)
        for docID in docIDSet:
            if docID in pl1set:
                pass
            else:
                result.append(docID)
        return result

    # --------------------------------------------------------------------------- #
    @classmethod
    def merge_ANDNOT(Index, Postinglist1: List[int], Postinglist2: List[int]) -> List[int]:
        result = []
        i = 0
        j = 0
        while i < len(Postinglist1) and j < len(Postinglist2):
            if Postinglist1[i] == Postinglist2[j]:
                i += 1
                j += 1
            elif Postinglist1[i] < Postinglist2[j]:
                result.append(Postinglist1[i])
                i += 1
            elif Postinglist1[i] > Postinglist2[j]:
                j += 1

        if i != len(Postinglist1):
            for x in range(i, len(Postinglist1)):
                result.append(Postinglist1[x])

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
    __slots__ = ('plist', 'seenDocIDs')

    def __init__(self, docID: str):
        # array.array
        # numpy array
        # oder liste
        self.plist = []
        self.seenDocIDs = set()
        # Sortierung!

        self.append(docID)

    def __len__(self):
        return len(self.plist)

    def __getitem__(self, idx):
        return self.plist[idx]

    # --------------------------------------------------------------------------- #
    def append(self, docID: str) -> None:
        if docID in self.seenDocIDs:
            pass
        else:
            self.plist.append(docID)
            self.seenDocIDs.add(docID)

    def final_sort(self) -> None:
        self.plist = sorted(self.plist)
        #, key=lambda x: int(x.split('-')[1]))


