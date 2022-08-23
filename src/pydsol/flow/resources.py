""" 
The code still needs lots of checks:
- existence of members
- double entry
- releasing more capacity than claimed
- registration of statistics in the model
- etc.
""" 

from abc import abstractmethod, ABC
from pydsol.core.statistics import SimTally, SimPersistent
from pydsol.core.interfaces import SimulatorInterface
from pydsol.core.utils import DSOLError
from _collections import OrderedDict
import math


class Queue(ABC):
    """
    """
    _counter: int = 0
        
    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf):
        """
        """
        self._simulator = simulator
        self._key = key
        self._name: str = name
        self._capacity: int = capacity
        self._members: OrderedDict = OrderedDict()
        self._entry_times: dict[object, float] = {}
        self._stat_length: SimPersistent = SimPersistent("QLEN_" + key,
                "Queue Length " + name, simulator)
        self._stat_qtime: SimTally = SimTally("QTIME_" + key,
                "Time in queue " + name, simulator)
    
    @abstractmethod
    def _add_impl(self, member: object):
        """
        """

    def add(self, member: object):
        """
        """
        if member in self._members:
            raise DSOLError("member " + str(member) + 
                " cannot be added to queue " + self._name + " twice") 
        self._add_impl(member)
        time: float = self._simulator.simulator_time
        self._entry_times[member] = time
        self._stat_length.register(time, self.length())

    @abstractmethod    
    def _remove_impl(self):
        """
        """
    
    def first(self) -> object:
        """
        """
        if self.length() == 0:
            return None
        member: object = self._remove_impl()
        time: float = self._simulator.simulator_time
        entry_time: float = self._entry_times.pop(member)
        self._stat_qtime.register(time - entry_time)
        self._stat_length.register(time, self.length())
        return object
    
    def length(self):
        """
        """
        return len(self._members)
    
    def members(self):
        """
        """
        return self._members.values()
    

class FifoQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf):
        """
        """
        super().__init__(key, name, simulator, capacity)
        
    def _add_impl(self, member: object):
        """
        """
        self._counter += 1
        self._members[(self._simulator.simulator_time, self._counter)] = member

    def _remove_impl(self):
        """
        """
        return self._members.popitem(False)[1]

    
class LifoQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf):
        """
        """
        super.__init__(key, name, simulator, capacity)
        
    def _add_impl(self, member: object):
        """
        """
        self._counter += 1
        self._members[(self._simulator.simulator_time, self._counter)] = member
        
    def _remove_impl(self):
        """
        """
        return self._members.popitem(True)[1]

    
class LVFQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf, attr_name: str = None):
        """
        """
        super.__init__(key, name, simulator, capacity)
        self._attr_name: str = attr_name
        
    def _add_impl(self, member: object):
        """
        """
        self._counter += 1
        self._members[(getattr(member, self._attr_namr), self._counter)] = member

    def _remove_impl(self):
        """
        """
        return self._members.popitem(False)[1]

    
class HVFQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf, attr_name: str = None):
        """
        """
        super.__init__(key, name, simulator, capacity)
        self._attr_name: str = attr_name
        
    def _add_impl(self, member: object):
        """
        """
        self._counter += 1
        self._members[(getattr(member, self._attr_namr), self._counter)] = member

    def _remove_impl(self):
        """
        """
        return self._members.popitem(True)[1]

    
class Resource:
    """
    """
    
    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=1, queue: Queue=None):
        """
        """
        self._simulator = simulator
        self._key: str = key
        self._name: str = name
        self._capacity: int = capacity
        self._initial_capacity = capacity
        self._members: set[object] = set()
        self._entry_times: dict[object, float] = {}
        self._claimed_capacity: dict[object, int] = {}
        self._stat_rutil: SimPersistent = SimPersistent("RUTIL_" + key,
                "Resource utilixation " + name, simulator)
        self._stat_rtime: SimTally = SimTally("RTIME_" + key,
                "Resource time " + name, simulator)
        if queue == None:
            self._queue: Queue = FifoQueue("Q_" + key, "Queue for " + name,
                                           simulator)
        else:
            self._queue = queue

    def seize(self, member: object, capacity: int=1):
        """
        """
        if self._capacity >= capacity:
            self._members.add(member)
            self._capacity -= capacity
            self._claimed_capacity[member] = capacity
            time: float = self._simulator.simulator_time
            self._entry_times[member] = time
            self._stat_rutil.register(time, self._initial_capacity 
                                      -self._capacity)
        else:
            self._queue.add(member)
        
    def release(self, member: object, capacity: int=1):
        """
        """
        self._claimed_capacity[member] -= capacity
        if self._claimed_capacity[member] <= 0:
            self._members.pop(member)
            self._claimed_capacity.pop(member)
            time: float = self._simulator.simulator_time
            claim_time: float = self._entry_times.pop(member)
            self._stat_rtime.register(time - claim_time)
        self._capacity += capacity
        self._stat_rutil.register(time, self._initial_capacity 
                                      -self._capacity)

