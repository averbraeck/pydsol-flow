"""
Test the utility classes and functions.
"""
from pydsol.flow.utils import SortedDict


def test_SortedDict():
    d: SortedDict = SortedDict()
    assert len(d) == 0
    assert d.first_key() == None
    assert d.last_key() == None
    assert d.first_value() == None
    assert d.last_value() == None
    assert d.first_item() == None
    assert d.last_item() == None
    
    d[10] = 'x'
    assert len(d) == 1
    assert d.first_key() == 10
    assert d.last_key() == 10
    assert d.first_value() == 'x'
    assert d.last_value() == 'x'
    assert d.first_item() == (10, 'x')
    assert d.last_item() == (10, 'x')
    
    d[20] = 'xx'
    d[5] = 'v'
    assert len(d) == 3
    assert d.first_key() == 5
    assert d.last_key() == 20
    assert d.first_value() == 'v'
    assert d.last_value() == 'xx'
    assert d.first_item() == (5, 'v')
    assert d.last_item() == (20, 'xx')
    
    d.pop(5)
    assert len(d) == 2
    assert d.first_key() == 10
    assert d.last_key() == 20
    assert d.first_value() == 'x'
    assert d.last_value() == 'xx'
    assert d.first_item() == (10, 'x')
    assert d.last_item() == (20, 'xx')


def test_SortedDict_init():
    d: SortedDict = SortedDict({10: 'j', 3: 'c', 1: 'a', 2: 'b', 5: 'e'})
    assert len(d) == 5
    assert d.first_key() == 1
    assert d.last_key() == 10
    assert d.first_value() == 'a'
    assert d.last_value() == 'j'
    assert d.first_item() == (1, 'a')
    assert d.last_item() == (10, 'j')
    
    d = d | {26: 'z', 25: 'y', 24: 'x'}
    assert len(d) == 8
    assert d.first_key() == 1
    assert d.last_key() == 26
    assert d.first_value() == 'a'
    assert d.last_value() == 'z'
    assert d.first_item() == (1, 'a')
    assert d.last_item() == (26, 'z')
    
