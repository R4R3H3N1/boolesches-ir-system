import os.path, sys
_this_path = os.path.dirname(os.path.realpath(__file__))
_parent_path = os.path.abspath( os.path.join( _this_path, '..' ) )
sys.path.append(_parent_path)

import indexer

def test_indexer():
    i = indexer.Index(os.path.join(os.getcwd(), 'tests', 'test_doc1.txt'))

    t_der = i.termClassMapping['der']
    t_das = i.termClassMapping['das']
    t_die = i.termClassMapping['die']

    assert i.dictionary[t_der].plist == [222]
    assert i.dictionary[t_das].plist == [111,222]

    assert i.dictionary[t_das].positions[111] == [1]
    assert i.dictionary[t_der].positions[222] == [3]
    assert i.dictionary[t_die].positions[222] == [5,6]

    assert i.dictionary[t_die].counts[222] == 2
    assert i.dictionary[t_das].counts[111] == 1


test_indexer()

