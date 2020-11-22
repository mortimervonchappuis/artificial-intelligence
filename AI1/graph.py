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
        lines.append('–+–'.join('–' * width for _ in range(len(nodes) + 1)))
        for from_node in nodes:
            lines.append(' ' * (max(0, width - len(str(from_node)))) + str(from_node).upper() + ' | ' + ' | '.join(str(self[from_node, to_node].cost).zfill(width) if self[from_node, to_node] is not None else '-' * width for to_node in nodes))
        return '\n'.join(lines)