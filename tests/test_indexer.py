import os.path, sys
_this_path = os.path.dirname(os.path.realpath(__file__))
_parent_path = os.path.abspath( os.path.join( _this_path, '..' ) )
sys.path.append(_parent_path)

import indexer, query_processing

def test_indexer():
    i = indexer.Index("io/ID.txt")

    q = query_processing.QueryProcessing(i)

    # germany   [822, 1114, 1242, 1530, 1755, 1757, 1963, 2633, 2654, 3793, 4403, 4418, 5138, 5148, 5369]




