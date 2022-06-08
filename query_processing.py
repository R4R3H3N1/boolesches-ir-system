from __future__ import annotations

import time

import indexer
import configuration


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
        print(f"INFO: Executing OR operation on {clause}")
        posting_list = self.index.dictionary[self.index.termClassMapping[clause.split("NOT")[1].strip()]]
        return self.index.merge_NOT(posting_list, self.index.documentIDs)

    # --------------------------------------------------------------------------- #
    def handle_term_and_prox_and_phrase_clause(self, clause: str) -> indexer.Postinglist:
        if self.is_proximity(clause):
            clause_split = [split.strip() for split in clause.split("\\")]
            term_one = clause_split[0]
            term_two = clause_split[1].split(" ")[1].strip()
            posting_list_one = self.get_posting_list_to_term(term_one)
            posting_list_two = self.get_posting_list_to_term(term_two)
            k = int(clause_split[1].split(" ")[0].strip())

            print(f"INFO: Executing proximity query on {term_one}, {term_two} and k = {str(k)}")
            result = self.index.proximity_query(posting_list_one, posting_list_two, k)

        elif self.is_phrase(clause):

            clause_split = [split.strip() for split in clause.split(" ")]

            if len(clause_split) == 2:
                term_one = clause_split[0].replace("\"", "").strip()
                term_two = clause_split[1].replace("\"", "").strip()

                posting_list1 = self.get_posting_list_to_term(term_one)
                posting_list2 = self.get_posting_list_to_term(term_two)

                print(f"INFO: Executing phrase query on {clause}")
                result = self.index.phrase_query(posting_list1, posting_list2)

            else:
                term_one = clause_split[0].replace("\"", "").strip()
                term_two = clause_split[1].strip()
                term_three = clause_split[2].replace("\"", "").strip()
                # TODO exceptions for single and double word queries

                posting_list1 = self.get_posting_list_to_term(term_one)
                posting_list2 = self.get_posting_list_to_term(term_two)
                posting_list3 = self.get_posting_list_to_term(term_three)

                print(f"INFO: Executing phrase query on {clause}")
                result = self.index.phrase_query(posting_list1, posting_list2, posting_list3)
        else:
            result = self.get_posting_list_to_term(term=clause)

        return result

    # --------------------------------------------------------------------------- #
    def get_posting_list_to_term(self, term) -> indexer.Postinglist:
        print(f"INFO: Retrieving Postinglist for term: {term}")
        result = indexer.Postinglist()
        try:
            result = self.index.dictionary[self.index.termClassMapping[term.strip()]]
        except KeyError:
            result = indexer.Postinglist()

        if len(result) <= configuration.R and configuration.KGRAM_INDEX_ENABLED:
            print(f"INFO: Activating Spell Checker for {term}")
            start = time.time()
            result = self.index.find_alternative_docids(term.strip())
            print(f"INFO: Spell checker took {round(time.time() - start, 3)} seconds.")

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
