import numpy as np

from typing import List


def jaccard_coefficient(list1: List, list2: List) -> float:
    set_a, set_b = set(list1), set(list2)
    try:
        return len(set_a.intersection(set_b)) / len(set_a.union(set_b))
    except ZeroDivisionError:
        return 0.0

def levenshtein_distance(src: str, tgt: str) -> int:
    deletion = 1
    insertion = 1
    def substitution(a,b):
        if a == b: return 0
        else: return 1

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
            dist[row][col] = min(dist[row-1][col]+deletion,
            dist[row-1][col-1]+substitution(src[row-1],tgt[col-1]),
            dist[row][col-1]+insertion)

    return int(dist[n][m])