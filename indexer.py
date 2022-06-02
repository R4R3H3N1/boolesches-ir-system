from tokenizer import tokenize_documents
import json

class Index:
    def __init__(self, filename: str):
        # dict[TermIndex, Postinglist]
        self.idx = {}
        self.termClassMapping = {}   # sollte auch bei index anfragen verwendet werden müssen
        # sort term, dann sort docid
        # sortieren term überspringen, da kein unterschied in dict?

        self.invoke_toknizer(filename)

    def invoke_toknizer(self, filename: str) -> None:
        try:
            with open(filename, 'r', encoding='utf8') as f:
                file = f.read()
                docs = file.split('\n')
        except FileNotFoundError:
            print(f'error opening file {filename}')
            return


        for docID, tokens in tokenize_documents(docs):
            for token in tokens:
                try:
                    ti = self.termClassMapping[token]
                except KeyError:
                    ti = TermIndex(token)
                    self.termClassMapping[token] = ti

                try:
                    self.idx[ti].append(docID)
                    ti.occurence += 1
                except KeyError:
                    self.idx[ti] = Postinglist(token)

        for key, val in self.idx.items():
            val.final_sort()

    def to_json(self) -> None:
        obj = {}
        for key, val in self.idx.items():
            obj.update({key.term:val.plist[1:10]})
        with open('index.json', 'w') as f:
            json.dump(obj, f)

    def from_json(self, filename: str) -> None:
        pass



class TermIndex:
    __slots__ = ('term', 'occurence')  # membervars hier hinzufügen

    def __init__(self, term: str):
        self.term = term
        self.occurence = 1

    def __hash__(self):
        return hash(self.term)


class Postinglist:
    __slots__ = ('plist', 'seenDocIDs')  # membervars hier hinzufügen

    def __init__(self, docID: str):
        # array.array
        # numpy array
        # oder liste
        self.plist = []
        self.seenDocIDs = set()
        # Sortierung!

        self.append(docID)

    def append(self, docID: str) -> None:
        if docID in self.seenDocIDs:
            pass
        else:
            self.plist.append(docID)
            self.seenDocIDs.add(docID)

    def final_sort(self) -> None:
        self.plist = sorted(self.plist)
