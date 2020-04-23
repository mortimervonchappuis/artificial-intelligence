class Node:
    def __init__(self, name, value=None, edges=[]) -> None:
        self.name = name
        self.value = value
        self.edges = edges
        self.successor = None
        self.cost = 0
    
    def reset(self, cost=0) -> None:
        self.successor = None
        self.cost = cost
    
    def set_successor(self, successor, cost) -> None:
        self.successor = successor
        self.cost = cost
    
    def children(self, key=None):
        if key is None:
            for edge in self.edges:
                if edge.parent == self:
                    yield edge.child
                elif edge.bidirectional:
                    if edge.parent == self:
                        yield edge.child
                    elif edge.child == self:
                        yield edge.parent
        else:
            return key in self.children()
    
    def parents(self, key=None):
        if key is not None:
            for edge in self.edges:
                if edge.child == self:
                    yield edge.parent
                elif edge.bidirectional:
                    if edge.parent == self:
                        yield edge.child
                    elif edge.child == self:
                        yield edge.parent
        else:
            key in self.children()
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
    
    def __neq__(self, other) -> bool:
        return not self == other
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f'Node({str(self)})'
    
    
class Edge:
    def __init__(self, parent: Node, child: Node, cost=1, bidirectional=True) -> None:
        self.child = child
        self.parent = parent
        self.cost = cost
        self.bidirectional = bidirectional
        if self not in self.child.edges:
            self.child.edges.append(self)
        if self not in self.parent.edges:
            self.parent.edges.append(self)
    
    def __str__(self) -> str:
        return f"{str(self.child)}{'<->' if self.bidirectional else '->'}{str(self.parent)}: {self.cost}"
    
    def __repr__(self) -> str:
        return f'Edge({str(self)})'
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Edge):
            return ((self.child == other.child and self.parent == other.parent) or (self.bidirectional and self.child == other.parent and self.parent == other.child)) and self.cost == other.cost
        elif isinstance(other, tuple):
            if len(other) == 2:
                return other == (self.child, self.parent) or self.bidirectional and other == (self.parent, self.child)
            elif len(other) == 3:
                return other == (self.child, self.parent, self.cost) or self.bidirectional and other == (self.parent, self.child, self.cost)

            
class Graph:
    def __init__(self, node_names: list, edges_stats: list, bidirectional=True) -> None:
        self.nodes = [Node(name) for name in node_names]
        self.edges = [Edge(self[parent], self[child], cost, bidirectional) for parent, child, cost in edges_stats]
        self.bidirectional = bidirectional
    
    def reset(self, value=0) -> None:
        for node in self.nodes:
            node.reset(value)
    
    def __getitem__(self, key) -> None:
        if isinstance(key, str):
            name = key
            for node in self.nodes:
                if node.name == name:
                    return node
        elif isinstance(key, tuple):
            parent, child = key
            for edge in self.edges:
                if edge.parent == parent and edge.child == child:
                    return edge
                elif self.bidirectional and edge.parent == child and edge.child == parent:
                    return edge
                
    def __str__(self) -> str:
        lines = []
        edge_max = max(self.edges,  key=lambda e: e.cost)
        name_max = max(self.nodes, key=lambda n: len(n.name))
        width = max(len(str(edge_max.cost)), len(name_max.name))
        nodes = sorted(self.nodes, key=lambda n: n.name)
        lines.append(' ' * width + ' | ' +  ' | '.join(' ' * (max(0, width - len(str(node)))) + str(node).upper() for node in nodes))
        lines.append('-+-'.join('-' * width for _ in range(len(nodes) + 1)))
        for from_node in nodes:
            lines.append(' ' * (max(0, width - len(str(from_node)))) + str(from_node).upper() + ' | ' + ' | '.join(str(self[from_node, to_node].cost).zfill(width) if self[from_node, to_node] is not None else '-' * width for to_node in nodes))
        return "\n".join(lines)


class Problem:
    def __init__(self, initial, target, goal=None):
        self.initial = initial
        self.target = target
        if goal is None:
            self.goal = lambda n: n == self.target or n.value == self.target or n.name == self.target
        else:
            self.goal = goal
    
    def __call__(self, node):
        return self.goal(node)


class Search:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
    
    def succession(self, node: Node, successors=[]) -> list:
        if node.successor is None:
            return [node] + successors
        else:
            return self.succession(node.successor, [node] + successors)
    
    def result(self, node: Node, reset_value=0) -> tuple:
        result = node.cost, self.succession(node)
        self.graph.reset(reset_value)
        return result
    
    def BFS(self, problem) -> tuple:
        self.graph.reset()
        node = self.graph[problem.initial]
        frontier, explored = [node], []
        while frontier:
            node = frontier.pop(0)
            explored.append(node)
            for child in node.children():
                if child not in explored and child not in frontier:
                    child.set_successor(node, node.cost + self.graph[node, child].cost)
                    if problem(child):
                        return self.result(child)
                    frontier.append(child)
    
    def DFS(self, problem) -> tuple:
        self.graph.reset()
        node = self.graph[problem.initial]
        frontier, explored = [node], []
        while frontier:
            node = frontier.pop()
            explored.append(node)
            for child in node.children():
                if child not in explored and child not in frontier:
                    child.set_successor(node, node.cost + self.graph[node, child].cost)
                    if problem(child):
                        return self.result(child)
                    frontier.append(child)
    
    def UCS(self, problem) -> tuple:
        self.graph.reset()
        node = self.graph[problem.initial]
        frontier, explored = list(node.children()), [node]
        for child in frontier:
            child.set_successor(node, self.graph[node, child].cost)
        frontier = sorted(frontier, key=lambda n: n.cost, reverse=False)
        while frontier:
            node = frontier.pop(0)
            if problem(node):
                return self.result(node)
            explored.append(node)
            for child in node.children():
                if child not in frontier and child not in explored:
                    child.set_successor(node, node.cost + self.graph[node, child].cost)
                    frontier = list(filter(lambda n: n.cost < child.cost, frontier)) + [child] + list(filter(lambda n: n.cost >= child.cost, frontier))
                elif child in frontier and frontier[(idx := frontier.index(child))].cost > child.cost:
                    child.set_successor(node, node.cost + self.graph[node, child].cost)
                    frontier[idx] = child


romania = Graph(
    ['Or', 'Ne', 'Ze', 'Ia', 'Ar', 'Si', 'Fa', 'Va', 'Ri', 'Ti',
     'Lu', 'Pi', 'Ur', 'Hi', 'Me', 'Bu', 'Dr', 'Ef', 'Cr', 'Gi'],
    [
        ('Or', 'Ze', 71), ('Or', 'Si', 151),
        ('Ne', 'Ia', 87), ('Ze', 'Ar', 75),
        ('Ia', 'Va', 92), ('Ar', 'Si', 140),
        ('Ar', 'Ti', 118), ('Si', 'Fa', 99),
        ('Si', 'Ri', 80), ('Fa', 'Bu', 211),
        ('Va', 'Ur', 142), ('Ri', 'Pi', 97),
        ('Ri', 'Cr', 146), ('Ti', 'Lu', 111),
        ('Lu', 'Me', 70), ('Me', 'Dr', 75),
        ('Dr', 'Cr', 120), ('Cr', 'Pi', 138),
        ('Pi', 'Bu', 101), ('Bu', 'Gi', 90),
        ('Bu', 'Ur', 85), ('Ur', 'Hi', 98),
        ('Hi', 'Ef', 86)
    ],)
print(romania)


S = Search(romania)
P = Problem(initial='Bu', target='Ti')

bfs_cost, bfs_path = S.BFS(P)
dfs_cost, dfs_path = S.DFS(P)
ucs_cost, ucs_path = S.UCS(P)

print(f"""
BFS: \t Cost = {bfs_cost} \t Path = {'->'.join(str(node) for node in bfs_path)}
DFS: \t Cost = {dfs_cost} \t Path = {'->'.join(str(node) for node in dfs_path)}
UCS: \t Cost = {ucs_cost} \t Path = {'->'.join(str(node) for node in ucs_path)}
""")

class Grid(Graph):
    def __init__(self, grid: str, node_code=' ', bidirectional=True):
        node_grid = [list(row) for row in grid.split('\n')]
        node_grid.reverse()
        nodes, edges = [], []
        for i, row in enumerate(node_grid):
            for j, v in enumerate(row): 
                if v == node_code:
                    nodes.append((i, j))
                    if i-1 >= 0 and node_grid[i-1][j] == node_code:
                        edges.append(((i-1, j), (i, j), 1))
                    if j-1 >= 0 and node_grid[i][j-1] == node_code:
                        edges.append(((i, j-1), (i, j), 1))
        self.i = i + 1
        self.j = j + 1
        self.code = grid
        self.bidirectional = bidirectional
        self.nodes = [Node(str(node), node) for node in nodes]
        self.edges = [Edge(self[str(parent)], self[str(child)], cost, bidirectional) for parent, child, cost in edges]
    
    def __str__(self):
        node_grid = [list(row) for row in self.code.split('\n')]
        return '# ' * (self.j + 2) + '\n# '+' #\n# '.join(' '.join(row) for row in node_grid) + ' #\n' + '# ' * (self.j + 2)
    
    def __repr__(self):
        return str(self)
    
    def __call__(self, path, symbol='*'):
        node_grid = [list(row) for row in self.code.split('\n')]
        for node in path:
            i, j = node.value
            node_grid[self.i - i - 1][j] = symbol
        return '# ' * (self.j + 2) + '\n# '+' #\n# '.join(' '.join(row) for row in node_grid) + ' #\n' + '# ' * (self.j + 2)


class A_STAR(Search):
    def __call__(self, problem, heuristic) -> tuple:
        self.graph.reset()
        h = lambda n: heuristic(n, problem)
        g = lambda n: n.cost
        f = lambda n: g(n) + h(n)
        c = lambda n, m: self.graph[n, m].cost
        closed = []
        opened = [problem.initial]
        while opened:
            node = opened.pop(0)
            print(node, list(node.children()))
            if problem(node):
                return self.result(node, float('inf'))
            closed.append(node)
            for child in node.children():
                if child not in closed and node not in opened:
                    child.reset(float('inf'))
                # Update Vertex
                if g(node) + c(node, child) < g(child):
                    child.set_successor(node, g(node) + c(node, child))
                    if child not in opened:
                        opened.append(child)
                    opened = sorted(opened, key=lambda n: f(n))


code_one = """   
 # 
   """
code_two = """   
   
   """
Grid_One = Grid(code_one)
for node in Grid_One.nodes:
    print(node, list(node.children()))

Grid_Two = Grid(code_two)
for node in Grid_One.nodes:
    print(node, list(node.children()))
    
print(f"""
Grid One

{str(Grid_One)}

Grid Two

{str(Grid_Two)}
""")

