import copy
from queue import Queue
from py2cfg import CFGBuilder

def pairwise(iterable):
    import itertools
    a,b = itertools.tee(iterable)
    next(b, None)
    return zip(a,b)

def get_nedges(cfg):
    start = cfg.entryblock
    q = Queue()
    n_edges = 0
    res = []
    v = list()
    q.put(start)
    while not q.empty():
        curr = q.get()
        n_edges += len(curr.exits)
        res.append((curr.at(), curr.end()))
        successors = [ block.target for block in curr.exits ]
        for x in successors:
            if x not in v:
                v.append(x)
                q.put(x)
    return n_edges


def _get_lineno_path(path):
    line_path = []
    for block in path:
        start, end = block.at(), block.end()
        line_path.append((start,end))
    return line_path

def _get_lineno_paths(paths):
    line_paths = []
    for path in paths:
        line_path = _get_lineno_path(path)
        line_paths.append(line_path)
    return line_paths

def explore_paths(cfg, flag=False):
    start = cfg.entryblock
    n_edges = get_nedges(cfg)
    paths = []
    visited = set()
    q = Queue()
    q.put([start])
    while not q.empty():
        # for i in range(q.qsize()):
            current_path = q.get()
            last_block = current_path[-1]
            successors = [ block.target for block in last_block.exits ]
            # successors = list({(item.at(),item.end()): item for item in successors}.values())
            for successor in successors:
                if successor in current_path: continue
                next_path = copy.copy(current_path)
                next_path.append(successor)
                if len(successor.exits) > 0:    # if successor is NOT a terminal node
                    line_path = _get_lineno_path(next_path)
                    # print(line_path)
                    q.put(next_path)
                else:
                    edges = [(x,y) for x,y in pairwise(next_path)]
                    if len( [ edge for edge in edges if edge not in visited ] ) > 0:
                        paths.append(next_path)
                        visited.update(set(edges))
                    if flag:
                        if len(visited) >= n_edges - 1:
                            line_paths = _get_lineno_paths(paths)
                            print(f"Visted edges: {len(visited)}")
                            return paths, line_paths
                        else:
                            v = [ (x.at(), y.at()) for x,y in visited ]
                            print(v)
                            print(f"Visted edges: {len(visited)} / {n_edges}")
    print(f"Visted edges: {len(visited)}")
    # v = [ (x.at(), y.at()) for x,y in visited ]
    # print(v)
    line_paths = _get_lineno_paths(paths)
    return paths, line_paths

def get_mut_paths(src_path, name='CFG_file'):
    methodDict = {}
    CFG_f = CFGBuilder(True).build_from_file(name, src_path)
    for name, CFG_m in CFG_f.functioncfgs.items():
        if name in [ '_decode_mixins', 'read_table_fits', '_encode_mixins']: continue
        mut_start, mut_end = CFG_m.lineno, CFG_m.end_lineno
        print(name, mut_start, mut_end, get_nedges(CFG_m))
        paths, line_paths = explore_paths(CFG_m)
        methodDict[name] = line_paths
    return methodDict

def get_lineno(block):
    return block.at(), block.end()

# if __name__ == '__main__':
#     src_path = '../astropy/astropy/io/fits/connect.py'
#     # get_mut_paths(src_path)
#     cfg = CFGBuilder(True).build_from_file('output', src_path)
#     fn_name = '_decode_mixins'
#     cfgm = cfg.functioncfgs[fn_name]
#     n_edges = get_nedges(cfgm)
#     print(n_edges)
#     paths, line_paths = explore_paths(cfgm)
#     print(line_paths)
