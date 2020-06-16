from collections import OrderedDict


class DotDict(OrderedDict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = DotDict(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DotDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DotDict, self).__delitem__(key)
        del self.__dict__[key]


class Iterator:
    """
    An custom iterator class to provide more functionality than the standard library iterator,
    more close to Java type iterators for full flexibility.
    """
    def __init__(self, iterable):
        """

        Parameters
        ----------
        iterable : Any storage containers that implement the methods __len__ and __getitem__.
        """
        for attr in ['__len__', '__getitem__']:
            if not hasattr(iterable, attr):
                raise TypeError('Argument iterable has no attribute {}.'.format(attr))

        self.data = iterable
        self.N = len(iterable)
        self.cursor = -1

    def peek(self):
        if not self.has_next():
            raise StopIteration()

        return self.data[self.cursor + 1]

    def has_next(self) -> bool:
        return self.cursor != self.N - 1

    def has_prev(self) -> bool:
        return self.cursor != 0

    def next(self):
        if not self.has_next():
            raise StopIteration()

        self.cursor += 1
        return self.data[self.cursor]

    def prev(self):
        if not self.has_prev():
            raise StopIteration()

        self.cursor -= 1
        return self.data[self.cursor]

    def item(self):
        return self.data[self.cursor]
