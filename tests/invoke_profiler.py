import os.path, sys, cProfile, pstats, timeit
_this_path = os.path.dirname(os.path.realpath(__file__))
_parent_path = os.path.abspath( os.path.join( _this_path, '..' ) )
sys.path.append(_parent_path)

import indexer, query_processing, configuration

def run():
    pr = cProfile.Profile()
    pr.enable()

    i = indexer.Index("../io/ID.txt")

    pr.disable()
    pr.dump_stats('profile')
    pstats.Stats('profile').strip_dirs().sort_stats('time').print_stats(15)

    q = query_processing.QueryProcessing(i)

    pr = cProfile.Profile()
    pr.enable()

    q.execute_query('\"is tat\" OR a AND is OR \"statistical office of the european commissions\" AND france \\5 germany')

    pr.disable()
    pr.dump_stats('profile')
    pstats.Stats('profile').strip_dirs().sort_stats('time').print_stats(15)

if __name__ == '__main__':
    run()

