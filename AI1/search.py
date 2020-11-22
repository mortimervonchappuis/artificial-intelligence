from graph import *
from copy import deepcopy


class Problem:
    def __init__(self, initial, target, goal=None) -> None:
        self.initial = initial
        self.target = target
        if goal is None:
            self.goal = lambda n: n == self.target or n.value == self.target or n.name == self.target
        else:
            self.goal = goal
    
    def __call__(self, node) -> bool:
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
    
    def BFS(self, problem: Problem) -> tuple:
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
    
    def DFS(self, problem: Problem) -> tuple:
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
    
    def UCS(self, problem: Problem) -> tuple:
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


class Grid(Graph):
    def __init__(self, grid: str, node_code=' ') -> None:
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
        self.bidirectional = True
        self.nodes = deepcopy([Node(str(node), node) for node in nodes])
        self.edges = deepcopy([Edge(self[str(parent)], self[str(child)], cost, self.bidirectional) for parent, child, cost in edges])
    
    def __str__(self) -> str:
        node_grid = [list(row) for row in self.code.split('\n')]
        return '× ' * (self.j + 2) + '\n× '+' ×\n× '.join(' '.join(row) for row in node_grid) + ' ×\n' + '× ' * (self.j + 2)
    
    def __repr__(self) -> str:
        return str(self)
    
    def __call__(self, path: list, symbol='·') -> str:
        node_grid = [list(row) for row in self.code.split('\n')]
        for node in path:
            i, j = node.value
            node_grid[self.i - i - 1][j] = symbol
        return '× ' * (self.j + 2) + '\n× '+' ×\n× '.join(' '.join(row) for row in node_grid) + ' ×\n' + '× ' * (self.j + 2)


class A_STAR(Search):
    def __call__(self, problem: Problem, heuristic) -> tuple:
        self.graph.reset()
        h = lambda n: heuristic(n, problem)
        g = lambda n: n.cost
        f = lambda n: g(n) + h(n)
        c = lambda n, m: self.graph[n, m].cost
        closed = []
        opened = [problem.initial]
        while opened:
            node = opened.pop(0)
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


euclidean = lambda n, p: sqrt((n.value[0] - p.target.value[0])**2 + (n.value[1] - p.target.value[1])**2)
manhatten = lambda n, p: n.value[0] - p.target.value[0] + n.value[1] - p.target.value[1]