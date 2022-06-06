import re

import indexer


class QueryProcessing:
    __slots__ = ('index')

    def __init__(self, index: indexer.Index):
        self.index = index

    def query(self, query_string):

        # Split after AND NOT clauses
        and_not_clauses = [split.strip() for split in query_string.split("AND NOT")]
        results = []

        # Split after AND clauses
        for and_not_clause in and_not_clauses:
            results.append(self.handle_and_clauses(and_not_clause))

    def handle_and_clauses(self, clause):

        and_clauses = [split.strip() for split in clause.split("AND")]
        results = []

        for and_clause in and_clauses:
            results.append(self.handle_or_clauses(clause))

        for i in range(len(results) - 1):
            results[i+1] = self.index.merge_AND(results[i], results[i+1])

        return results[len(results) - 1]

    def handle_or_clauses(self, clause):

        or_clauses = [split.strip() for split in clause.split("OR")]
        results = []

        for or_clause in or_clauses:
            results.append(self.handle_low_level_clauses(or_clause))

        return results[len(results) - 1]

    def handle_low_level_clauses(self, clause):

        result = []

        if "NOT" in clause:
            result = self.handle_not_clause(clause)
        else:
            result = self.handle_term_and_prox_and_phrase_clause(clause)

        return result

    def handle_not_clause(self, clause):
        posting_list = self.index.dictionary[self.index.termClassMapping[clause]]
        return self.index.merge_NOT(posting_list, self.index.documentIDs)

    def handle_term_and_prox_and_phrase_clause(self, clause):

        result = []

        if self.is_proximity(clause):
            clause_split = [split.strip() for split in clause.split("\\")]
            term_one = clause_split[0]
            k = int(clause_split[1].split(" ")[0].strip())
            term_two = clause_split[1].split(" ")[1].strip()
            result = self.index.proximity_query(term_one, term_two, k)
        elif self.is_phrase(clause):
            clause_split = [split.strip() for split in clause.split(" ")]
            if len(clause_split) == 2:
                term_one = clause_split[0].replace("\"", "").strip()
                term_two = clause_split[1].replace("\"", "").strip()
                result = self.index.phrase_query(term_one, term_two)
            else:
                term_one = clause_split[0].replace("\"", "").strip()
                term_two = clause_split[1].strip()
                term_three = clause_split[2].replace("\"", "").strip()
                result = self.index.phrase_query(term_one, term_two, term_three)
        else:
            result = self.index.dictionary[self.index.termClassMapping[clause.strip()]]

        return result

    @staticmethod
    def is_proximity(self, clause):
        if "\\" in clause:
            return True
        else:
            return False

    @staticmethod
    def is_phrase(self, clause):
        if "\"" in clause:
            return True
        else:
            return False
        