from __future__ import annotations
import numpy as np

from typing import List, Set
import configuration
import indexer


def jaccard_coefficient(list1: List, list2: List) -> float:
    set_a, set_b = set(list1), set(list2)
    try:
        return len(set_a.intersection(set_b)) / len(set_a.union(set_b))
    except ZeroDivisionError:
        return 0.0


def levenshtein_distance(src: str, tgt: str) -> int:
    deletion = 1
    insertion = 1

    def substitution(a, b):
        if a == b:
            return 0
        else:
            return 1

    n = len(src)
    m = len(tgt)
    dist = np.zeros((n+1, m+1))
    dist[0][0] = 0

    for row in range(1, n+1):   # range() not inclusive
        dist[row][0] = dist[row-1][0] + deletion

    for col in range(1, m+1):
        dist[0][col] = dist[0][col-1] + insertion

    for row in range(1, n+1):
        for col in range(1, m+1):
            dist[row][col] = min(dist[row-1][col] + deletion, dist[row-1][col-1] + substitution(src[row-1], tgt[col-1]),
                                 dist[row][col-1] + insertion)

    return int(dist[n][m])


# --------------------------------------------------------------------------- #
def phrase_query(posting_list1: indexer.Postinglist, posting_list2: indexer.Postinglist,
                 posting_list3: indexer.Postinglist = None) -> indexer.Postinglist:

    result = indexer.Postinglist()

    if posting_list3 is None:
        candidates = merge_AND(posting_list1, posting_list2)

        for docID in candidates:
            for pos1 in posting_list1.positions[docID]:
                for pos2 in posting_list2.positions[docID]:
                    if pos1 == pos2 - 1 and docID not in result:
                        result.append(docID, -1)
    else:
        candidates = merge_AND(merge_AND(posting_list1, posting_list2), posting_list3)

        for docID in candidates:
            for pos1 in posting_list1.positions[docID]:
                for pos2 in posting_list2.positions[docID]:
                    for pos3 in posting_list3.positions[docID]:
                        if pos1 == pos2 - 1 and pos2 == pos3 - 1 and docID not in result:
                            result.append(docID, -1)

    return result


# --------------------------------------------------------------------------- #
def proximity_query(posting_list1: indexer.Postinglist, posting_list2: indexer.Postinglist, k: int = 1) \
        -> indexer.Postinglist:

    candidates = merge_AND(posting_list1, posting_list2)
    result = indexer.Postinglist()

    for docID in candidates:
        for pos1 in posting_list1.positions[docID]:
            for pos2 in posting_list2.positions[docID]:
                if abs(pos1-pos2) <= k and docID not in result:
                    result.append(docID, -1)

    return result


# --------------------------------------------------------------------------- #
def merge_AND(posting_list1: indexer.Postinglist, posting_list2: indexer.Postinglist) -> indexer.Postinglist:
    i, j = 0, 0
    result = indexer.Postinglist()

    while i < len(posting_list1) and j < len(posting_list2):
        if posting_list1[i] == posting_list2[j]:
            result.append(posting_list1[i], posting_list1.positions[posting_list1[i]] +
                          posting_list2.positions[posting_list2[j]])
            i += 1
            j += 1
        else:
            if posting_list1[i] < posting_list2[j]:
                if configuration.ACTIVATE_SKIP_POINTER:
                    try:
                        if posting_list1[posting_list1.skip_pointer[posting_list1[i]]] \
                                <= posting_list2[j]:
                            i = posting_list1.skip_pointer[posting_list1[i]]
                        else:
                            i += 1
                    except KeyError:
                        i += 1
                else:
                    i += 1
            else:
                if configuration.ACTIVATE_SKIP_POINTER:
                    try:
                        if posting_list2[posting_list2.skip_pointer[posting_list2[j]]] \
                                <= posting_list1[i]:
                            j = posting_list2.skip_pointer[posting_list2[j]]
                        else:
                            j += 1
                    except KeyError:
                        j += 1
                else:
                    j += 1
    return result


# --------------------------------------------------------------------------- #
def merge_OR(posting_list1: indexer.Postinglist, posting_list2: indexer.Postinglist) -> indexer.Postinglist:
    result = indexer.Postinglist()
    i, j = 0, 0
    while i < len(posting_list1) and j < len(posting_list2):
        if posting_list1[i] == posting_list2[j]:
            result.append(posting_list1[i], posting_list1.positions[posting_list1[i]] +
                          posting_list2.positions[posting_list2[j]])
            i += 1
            j += 1
        elif posting_list1[i] < posting_list2[j]:
            result.append(posting_list1[i], posting_list1.positions[posting_list1[i]])
            i += 1
        elif posting_list1[i] > posting_list2[j]:
            result.append(posting_list2[j], posting_list2.positions[posting_list2[j]])
            j += 1

    if i != len(posting_list1):
        for x in range(i, len(posting_list1)):
            result.append(posting_list1[x], posting_list1.positions[posting_list1[x]])
    if j != len(posting_list2):
        for x in range(j, len(posting_list2)):
            result.append(posting_list2[x], posting_list2.positions[posting_list2[x]])

    return result


# --------------------------------------------------------------------------- #
def merge_NOT(posting_list1: indexer.Postinglist, docIDSet: Set[int]) -> indexer.Postinglist:
    result = indexer.Postinglist()

    pl1set = set(posting_list1.plist)
    for docID in docIDSet:
        if docID in pl1set:
            pass
        else:
            # TODO: why str() ?
            result.append(str(docID), -1)
    return result


# --------------------------------------------------------------------------- #
def merge_ANDNOT(posting_list1: indexer.Postinglist, posting_list2: indexer.Postinglist) -> indexer.Postinglist:
    result = indexer.Postinglist()
    i = 0
    j = 0
    while i < len(posting_list1) and j < len(posting_list2):
        if posting_list1[i] == posting_list2[j]:
            i += 1
            j += 1
        elif posting_list1[i] < posting_list2[j]:
            result.append(posting_list1[i], posting_list1.positions[posting_list1[i]])
            i += 1
        elif posting_list1[i] > posting_list2[j]:
            if configuration.ACTIVATE_SKIP_POINTER:
                try:
                    if posting_list2[posting_list2.skip_pointer[posting_list2[j]]] \
                            <= posting_list1[i]:
                        j = posting_list2.skip_pointer[posting_list2[j]]
                    else:
                        j += 1
                except KeyError:
                    j += 1
            else:
                j += 1

    if i != len(posting_list1):
        for x in range(i, len(posting_list1)):
            result.append(posting_list1[x], posting_list1.positions[posting_list1[x]])

    return result

