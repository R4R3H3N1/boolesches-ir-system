import os.path, sys
_this_path = os.path.dirname(os.path.realpath(__file__))
_parent_path = os.path.abspath( os.path.join( _this_path, '..' ) )
sys.path.append(_parent_path)

import indexer

pl1 = [1,3,4,5,7]
pl2 = [1,2,3,6,8,10]

mainset = set([1,2,3,4,5,6,7,8,9,10])

def test_AND():
    res = indexer.Index.merge_AND(pl1, pl2)
    assert res == [1,3]

def test_OR():
    res = indexer.Index.merge_OR(pl1, pl2)
    assert res == [1,2,3,4,5,6,7,8,10]

def test_NOT():
    res = indexer.Index.merge_NOT(pl1, mainset)
    assert res == [2,6,8,9,10]

def test_ANDNOT():
    res = indexer.Index.merge_ANDNOT(pl1, pl2)
    assert res == [4,5,7]

