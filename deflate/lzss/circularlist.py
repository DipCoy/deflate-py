class CircularIterator:
    def __init__(self, list_: 'CircularList'):
        self.list_ = list_
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.list_):
            raise StopIteration

        o = self.list_[self.current]
        self.current += 1
        return o


class CircularList(object):
    def __init__(self, size):
        """Initialization"""
        self.index = 0
        self.size = size
        self._data = []

    def append(self, value):
        """Append an element"""
        if len(self._data) == self.size:
            self._data[self.index] = value
        else:
            self._data.append(value)
        self.index = (self.index + 1) % self.size

    def __iter__(self):
        return CircularIterator(self)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        """Get element by index, relative to the current index"""
        if len(self._data) == self.size:
            return self._data[(key + self.index) % self.size]
        else:
            return self._data[key]

    def slice(self, start: int, end: int):
        r = list(self)
        return r[start: end]

    def __repr__(self):
        """Return string representation"""
        return (self._data[self.index:] + self._data[:self.index]).__repr__() + ' (' + str(len(self._data))+'/{} items)'.format(self.size)
