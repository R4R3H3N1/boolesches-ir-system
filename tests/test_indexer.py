import os.path, sys
_this_path = os.path.dirname(os.path.realpath(__file__))
_parent_path = os.path.abspath( os.path.join( _this_path, '..' ) )
sys.path.append(_parent_path)

import indexer, query_processing, configuration

def test_indexer():
    assert configuration.KGRAM_INDEX_ENABLED == True
    assert configuration.R == 3
    assert configuration.K == 3
    assert configuration.J == 0.2
    assert configuration.MAX_LEVENSHTEIN_DISTANCE == 2

    i = indexer.Index("io/ID.txt")

    q = query_processing.QueryProcessing(i)

    assert q.execute_query('germany').plist == [822, 1114, 1242, 1530, 1755, 1757, 1963, 2633, 2654, 3793, 4403, 4418, 5138, 5148, 5369]
    assert q.execute_query('germany AND NOT eu').plist == [822, 1114, 1242, 1530, 1755, 1757, 1963, 2633, 2654, 3793, 4403, 4418, 5138, 5148]
    assert q.execute_query('germany AND eu').plist == [5369]

    assert q.execute_query('eu AND NOT germany').plist == [333, 806, 815, 1753, 2392, 2399, 2407, 3066, 3081, 3090, 3773, 4406, 4437, 4747, 4910, 4912, 5253]

    assert q.execute_query('\"statistical office of the european commissions\"').plist == [5369]
    assert q.execute_query('france \\5 germany').plist == [1114, 3793, 4403]
    assert q.execute_query('\"statistical office of the european commissions\" OR france \\5 germany').plist == [1114, 3793, 4403, 5369]

    assert q.execute_query('france \\5 germany AND NOT \"hodgkin lymphoma\"').plist == [3793, 4403]

    assert q.execute_query('france \\5 germany AND NOT \"hogkin lympoma\"').plist == [3793, 4403]
    assert i.find_term_alternatives('hogkin') == ['hodgkin']
    assert [term in ['lymphoma', 'lymphomas'] for term in i.find_term_alternatives('lympoma')]





