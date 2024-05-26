from collections import defaultdict
from typing import Optional

from deflate.suffix_tree.circularlist import CircularList


class Node:
    text = ""  # for debug purpose

    def __init__(self, edges=None, suff_link=None, parent=None):
        self.edges = edges if edges is not None else defaultdict(type(None))
        self.suff_link: Optional[Node] = suff_link
        self.parent: Optional[Node] = parent

    def __str__(self):
        if self.parent:
            idxs = [e.idxs for e in self.parent.edges.values() if e.target_node == self][0]
            return f"{self.parent}{self.text[idxs[0]: idxs[1]]}_"
        else:
            return "_"


class Edge:
    def __init__(self, idxs=None, target_node=None):
        self.idxs = idxs
        self.target_node: Optional[Node] = target_node


class SuffixTree:
    # node =  < suffix_link, parent, edges >
    # edges = { first_char => edge }
    # edge =  < idxs, target_node >
    # idxs = (first, last) # corresponds to label = text[first: last]
    def __init__(self, text, window_size: int):
        self.__buffer = CircularList(window_size)
        self.joker_edge = Edge(idxs=(0, 1))
        self.joker = Node(edges=defaultdict(lambda: self.joker_edge))
        self.root = Node(suff_link=self.joker)
        self.joker_edge.target_node = self.root
        self.infty = 0
        self.__builder = None
        self.add(text)

    def add(self, s: str):
        for i, c in enumerate(s):
            self.__buffer.append(c)
            self.infty += 1

            if self.__builder is None:
                self.__builder = self._build_tree(self.root, 0, self.infty, generator=True)

            self.__builder.__next__()
        #self._build_tree(self.root, 0, self.infty)

    def __str__(self):
        text_ = ''.join(self.__buffer)
        return f"SuffixTree(text='{text_}')"

    def pp(self, node=None, indent=0):
        node = node or self.root
        space = "    " * indent
        print(space + f"ID    : {node}")
        print(space + f"link  : {node.suff_link}")
        print(space + f"edges : ")

        for c, edge in node.edges.items():
            print(space + f"  -{c} {edge.idxs}={self.__buffer.slice(edge.idxs[0], edge.idxs[1])}:")
            self.pp(edge.target_node, indent + 1)

    def find(self, substring: str) -> int:
        node = self.root
        last_edge = None
        current_substring_index = 0
        for s in substring:
            if node is None:
                return -1

            if s not in node.edges:
                break

            last_edge = node.edges[s]
            node = last_edge.target_node

        if last_edge is None:
            return -1

        if len(substring) > last_edge.idxs[1] - last_edge.idxs[0] + 1:
            return -1

        for s_i, e_i in zip(range(len(substring)), range(last_edge.idxs[0], last_edge.idxs[1] + 1)):
            if substring[s_i] != self.__buffer[e_i]:
                return -1

        return last_edge.idxs[0]

    def _build_tree(self, node: Node, n: int, infty: int, skip: int = 0, generator: bool = False):
        def stop() -> bool:
            if generator:
                return False
            return n >= infty

        while not stop():
            c = self.__buffer[n]
            edge = node.edges[c]

            if edge is None:  # no way to go; creating new leaf
                new_leaf = Node(parent=node)
                node.edges[c] = Edge(idxs=(n, self.infty), target_node=new_leaf)
                node = node.suff_link
                continue

            first, last = edge.idxs
            i, n0 = first, n
            if skip > 0:
                can_skip = min(skip, last - first)
                i += can_skip
                n += can_skip
                skip -= can_skip

            while (
                    i < last and n < infty and
                    (self.__buffer[i] == self.__buffer[n] or edge is self.joker_edge)
            ):
                i += 1
                n += 1

            if i == last:  # go to the next node
                node = edge.target_node
                if generator:
                    yield
                continue
            # splitting edge
            middle_node = Node(parent=node)
            middle_node.edges[self.__buffer[i]] = edge
            node.edges[c] = Edge(idxs=(first, i), target_node=middle_node)
            edge.idxs = (i, edge.idxs[1])
            edge.target_node.parent = middle_node
            t = None
            for _ in self._build_tree(node.suff_link, n0, n, i - first):
                t = _
            middle_node.suff_link = t
            node = middle_node
        yield node


text = "abrakadabra"
first = "abrakad"
second = "abra"
# text = "abca"
Node.text = text
tree = SuffixTree('', 200)
tree.add(first)
#tree.add(second)
# l = tree.find('kad')
# l = tree.find('raka')
# print(l)
tree.pp()
