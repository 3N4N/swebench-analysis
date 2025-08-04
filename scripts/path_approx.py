import copy
import inspect
from queue import Queue
from python_graphs import control_flow
from python_graphs import control_flow_graphviz as cfgviz
from python_graphs import cyclomatic_complexity

from astropy.io.fits import connect

module = connect

def is_mod_function(mod, func):
    return inspect.isfunction(func) and inspect.getmodule(func) == mod


def list_functions(mod):
    return {name: obj for name,obj in inspect.getmembers(module, inspect.isfunction)
            if is_mod_function(mod,obj)}

def bfs(cfg):
    blocks = cfg.blocks
    start = cfg.start_block
    visited = []
    res = []
    q = Queue()
    q.put(start)
    while not q.empty():
        curr = q.get()
        res.append(curr)
        for x in curr.next:
            if x not in visited:
                visited.append(x)
                q.put(x)
    return res

def pairwise(iterable):
    import itertools
    a,b = itertools.tee(iterable)
    next(b, None)
    return zip(a,b)

def explore_paths(cfg):
    start = [block for block in cfg.blocks if block.label.startswith('<entry:')][0]
    ends = [ block for block in cfg.blocks if len(block.next)==0 ]
    n_edges = sum( [ len(block.next) for block in cfg.blocks ] ) - 2    # <start> -> <raise>, <start> -> <exit>
    method_paths = []
    visited = set()
    q = Queue()
    q.put([start])
    while not q.empty():
        for i in range(q.qsize()):
            current_path = q.get()
            last_node = current_path[-1]
            for successor in last_node.next:
                next_path = copy.copy(current_path)
                next_path.append(successor)
                if successor not in ends:
                    q.put(next_path)
                else:
                    edges = [(x,y) for x,y in pairwise(next_path)]
                    if len( [ edge for edge in edges if edge not in visited ] ) > 0:
                        method_paths.append(next_path)
                        visited.update(set(edges))
                    if len(visited) == n_edges:
                        return method_paths
                    else:
                        print(n_edges, len(visited))

for path in paths:
    for block in path:
        print(block.label)
    print()

def get_mut_paths(module):
    methodDict = {}
    funcs = list_functions(module)
    for fn_name, fn_obj in funcs.items():
        cfg = control_flow.get_control_flow_graph(fn_obj)
        cyc = cyclomatic_complexity.cyclomatic_complexity(cfg)
        print(f"{fn_name} : {cyc}, {len(cfg.blocks)}, {len(cfg.nodes)}")
        paths = explore_paths(cfg)
        methodDict[cyc] = paths
    return methodDict
