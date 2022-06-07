from __future__ import annotations
import indexer
from configuration import *


class QueryProcessing:
    __slots__ = ('index')

    # --------------------------------------------------------------------------- #
    def __init__(self, index):
        self.index = index

    # --------------------------------------------------------------------------- #
    def execute_query(self, query_string: str) -> indexer.Postinglist:
        # Split after AND NOT clauses
        and_not_clauses = [split.strip() for split in query_string.split("AND NOT")]
        results = []

        # Split after AND clauses
        for and_not_clause in and_not_clauses:
            results.append(self.handle_and_clauses(and_not_clause))

        # Execute all AND NOT clauses
        for i in range(len(results) - 1):
            print("INFO: Executing AND NOT operation")
            results[i + 1] = self.index.merge_ANDNOT(results[i], results[i+1])

        return results[len(results) - 1]

    # --------------------------------------------------------------------------- #
    def handle_and_clauses(self, clause: str) -> indexer.Postinglist:
        # Split after AND clauses
        and_clauses = [split.strip() for split in clause.split("AND")]
        results = []

        # Handle OR clauses inside the AND clauses
        for and_clause in and_clauses:
            results.append(self.handle_or_clauses(and_clause))

        # Execute all AND clauses
        for i in range(len(results) - 1):
            print("INFO: Executing AND operation")
            results[i+1] = self.index.merge_AND(results[i], results[i+1])

        return results[len(results) - 1]

    # --------------------------------------------------------------------------- #
    def handle_or_clauses(self, clause: str) -> indexer.Postinglist:

        # Split after all OR clauses
        or_clauses = [split.strip() for split in clause.split("OR")]
        results = []

        # Handle all low level clauses
        for or_clause in or_clauses:
            results.append(self.handle_low_level_clauses(or_clause))

        # Execute all OR clauses
        for i in range(len(results) - 1):
            print("INFO: Executing OR operation")
            results[i + 1] = self.index.merge_OR(results[i], results[i+1])

        return results[len(results) - 1]

    # --------------------------------------------------------------------------- #
    def handle_low_level_clauses(self, clause: str) -> indexer.Postinglist:

        if "NOT" in clause:
            result = self.handle_not_clause(clause)
        else:
            result = self.handle_term_and_prox_and_phrase_clause(clause)

        return result

    # --------------------------------------------------------------------------- #
    def handle_not_clause(self, clause: str) -> indexer.Postinglist:
        print("INFO: Executing OR operation on " + clause)
        posting_list = self.index.dictionary[self.index.termClassMapping[clause.split("NOT")[1].strip()]]
        return self.index.merge_NOT(posting_list, self.index.documentIDs)

    # --------------------------------------------------------------------------- #
    def handle_term_and_prox_and_phrase_clause(self, clause: str) -> indexer.Postinglist:
        if self.is_proximity(clause):
            clause_split = [split.strip() for split in clause.split("\\")]
            term_one = clause_split[0]
            k = int(clause_split[1].split(" ")[0].strip())
            term_two = clause_split[1].split(" ")[1].strip()
            print("INFO: Executing proximity query on " + term_one + ", " + term_two + " and k = " + str(k))
            result = self.index.proximity_query(term_one, term_two, k)
        elif self.is_phrase(clause):
            clause_split = [split.strip() for split in clause.split(" ")]
            print("INFO: Executing phrase query on " + clause)
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
            print("INFO: Retrieving docIDs for term: " + clause)
            try:
                result = self.index.dictionary[self.index.termClassMapping[clause.strip()]]
            except KeyError:
                result = []

            if len(result) <= R:
                print("INFO: Activating Spell Checker for {clause}")
                result = self.index.find_alternative_docids(clause.strip())

        return result

    # --------------------------------------------------------------------------- #
    @staticmethod
    def is_proximity(clause: str) -> bool:
        if "\\" in clause:
            return True
        else:
            return False

    # --------------------------------------------------------------------------- #
    @staticmethod
    def is_phrase(clause: str) -> bool:
        if "\"" in clause:
            return True
        else:
            return False
