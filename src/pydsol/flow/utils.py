"""
Utility functions and classes for pydsol-flow.
"""
from collections import UserDict


class SortedDict(UserDict):
    """
    Functionality of the OrderedDict that keeps the dictionary sorted on the
    keys at all times. Additionally, functions for first and last key, first
    and last value, and first and last key-value pair have been added. 
    """
    
    def __init__(self, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)
        self.data = dict(sorted(self.data.items()))
    
    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        self.data = dict(sorted(self.data.items()))

    def __or__(self, other):
        return SortedDict(UserDict.__or__(self, other))
    
    def __ror__(self, other):
        return SortedDict(UserDict.__ror__(self, other))

    def __ior__(self, other):
        return SortedDict(UserDict.__ior__(self, other))
    
    def first_key(self):
        if len(self.data) == 0:
            return None
        return next(iter(self.data))
    
    def last_key(self):
        if len(self.data) == 0:
            return None
        return next(reversed(self.data))
    
    def first_value(self):
        if len(self.data) == 0:
            return None
        return self.data[self.first_key()]
    
    def last_value(self):
        if len(self.data) == 0:
            return None
        return self.data[self.last_key()]
    
    def first_item(self):
        if len(self.data) == 0:
            return None
        return next(iter(self.data.items()))
    
    def last_item(self):
        if len(self.data) == 0:
            return None
        return next(reversed(self.data.items()))

