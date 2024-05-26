import queue

from deflate.suffix_tree.node import Node


class UkkonenSuffixTreeBuilder:
    def __init__(self):
        self.__root_node = Node(symbols=[], children=[])

    def append(self, substring: str):
        for i in range(len(substring) + 1):
            for j in range(i):
                s = substring[j:i]
                self.__extend(s)

    def __extend(self, s: str):
        q = queue.Queue()
        q.put_nowait(self.__root_node)

        nodes = []
        while q.not_empty:
            n = q.get_nowait()
            nodes.append(n)
            for c in n.childre:
                q.put_nowait(c)

        for node in nodes:
            ...


UkkonenSuffixTreeBuilder().append('abcd')
