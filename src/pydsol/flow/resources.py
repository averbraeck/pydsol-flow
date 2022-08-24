""" 
The code still needs lots of checks:
- existence of members
- double entry
- releasing more capacity than claimed
- registration of statistics in the model
- etc.
""" 

from abc import abstractmethod, ABC
import math
from typing import Callable, Any

from attr import dataclass
from pydsol.core.interfaces import SimulatorInterface
from pydsol.core.statistics import SimTally, SimPersistent
from pydsol.core.utils import DSOLError
from pydsol.flow.utils import SortedDict


class Queue(ABC):
    """
    """
    _counter: int = 0
        
    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf, last: bool=False):
        """
        """
        self._simulator = simulator
        self._key = key
        self._name: str = name
        self._capacity: int = capacity
        self._last = last
        self._members: SortedDict[object, object] = SortedDict()
        self._entry_times: dict[object, float] = {}
        self._stat_length: SimPersistent = SimPersistent("QLEN_" + key,
                "Queue Length " + name, simulator)
        self._stat_qtime: SimTally = SimTally("QTIME_" + key,
                "Time in queue " + name, simulator)
    
    @abstractmethod
    def _sorting_key(self, member: object) -> object:
        """
        """

    def add(self, member: object):
        """
        """
        if member in self._members:
            raise DSOLError("member " + str(member) + 
                " cannot be added to queue " + self._name + " twice") 
        key = self._sorting_key(member)
        print("Key = " + str(key))
        self._members[key] = member
        time: float = self._simulator.simulator_time
        self._entry_times[member] = time
        self._stat_length.register(time, self.length())

    def remove_first(self) -> object:
        """
        """
        if self.length() == 0:
            return None
        if self._last:
            member: object = self._members.pop(self._members.last_key())
        else:
            member: object = self._members.pop(self._members.first_key())
        time: float = self._simulator.simulator_time
        entry_time: float = self._entry_times.pop(member)
        self._stat_qtime.register(time - entry_time)
        self._stat_length.register(time, self.length())
        return member
 
    def peek_first(self) -> object:
        """
        """
        if self.length() == 0:
            return None
        if self._last:
            return self._members.last_value()
        return self._members.first_value()
    
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
        super().__init__(key, name, simulator, capacity, True)
        
    def _sorting_key(self, member: object) -> object:
        """
        """
        print("REQUEST")
        self._counter += 1
        return (self._simulator.simulator_time, self._counter)

   
class LifoQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf):
        """
        """
        super.__init__(key, name, simulator, capacity, False)
        
    def _sorting_key(self, member: object):
        """
        """
        self._counter += 1
        return (self._simulator.simulator_time, self._counter)
        
    
class LVFQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf, attr_name: str=None):
        """
        """
        super.__init__(key, name, simulator, capacity, False)
        self._attr_name: str = attr_name
        
    def _sorting_key(self, member: object):
        """
        """
        self._counter += 1
        return (getattr(member, self._attr_namr), self._counter)

    
class HVFQueue(Queue):
    """
    """

    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int=math.inf, attr_name: str=None):
        """
        """
        super.__init__(key, name, simulator, capacity, True)
        self._attr_name: str = attr_name
        
    def _sorting_key(self, member: object):
        """
        """
        self._counter += 1
        return (getattr(member, self._attr_namr), self._counter)


@dataclass
class ResourceRequest():
    """
    """
    requestor: object = None
    requested_capacity: int = None
    claimed_capacity: int = None
    entry_time: float = None
    start_time: float = None
    callback: Callable = None
    callback_args: list[Any] = None
    callback_kwargs: dict[str, Any] = None

    
class Resource:
    """
    """
    
    def __init__(self, key: str, name: str, simulator: SimulatorInterface,
                 capacity: int, queue: Queue=None):
        """
        """
        self._simulator = simulator
        self._key: str = key
        self._name: str = name
        self._capacity: int = capacity
        self._initial_capacity = capacity
        self._waiting: dict[object, ResourceRequest] = {}
        self._processing: dict[object, ResourceRequest] = {}
        self._stat_rutil: SimPersistent = SimPersistent("RUTIL_" + key,
                "Resource utilization " + name, simulator)
        self._stat_rtime: SimTally = SimTally("RTIME_" + key,
                "Resource time " + name, simulator)
        if queue == None:
            self._queue: Queue = FifoQueue("Q_" + key, "Queue for " + name,
                                           simulator)
        else:
            self._queue = queue

    def _allocate_capacity(self, request: ResourceRequest):
        """
        """
        time: float = self._simulator.simulator_time
        self._capacity -= request.requested_capacity
        self._stat_rutil.register(time, self._initial_capacity - self._capacity)
        self._waiting.pop(request.requestor, None)
        self._processing[request.requestor] = request
        request.claimed_capacity = request.requested_capacity
        request.start_time = time
        print(request.requestor + " has start_time " + str(request.start_time))
        request.callback(*request.callback_args, **request.callback_kwargs)
        
    def seize(self, requestor: object, requested_capacity: int,
              callback: Callable, *args, **kwargs):
        """
        """
        time: float = self._simulator.simulator_time
        request: ResourceRequest = ResourceRequest()
        request.requestor = requestor
        request.requested_capacity = requested_capacity
        request.entry_time = time
        request.start_time = None
        request.callback = callback
        request.callback_args = args
        request.callback_kwargs = kwargs
           
        if self._capacity >= requested_capacity:
            self._allocate_capacity(request)
        else:
            self._waiting[request.requestor] = request
            self._queue.add(requestor)
        print("End of Seize: cap=" + str(self._capacity))
        print("Seize Queue : " + str(self._queue._members))
        print("Processing Queue : " + str(self._processing.keys()))
        
    def release(self, requestor: object, capacity: int=1):
        """
        """
        print("Release: item=" + str(requestor))
        print("Release: cap=" + str(self._capacity))
        time: float = self._simulator.simulator_time
        request: ResourceRequest = self._processing[requestor]
        print(request.requestor + " has start_time " + str(request.start_time))
        request.claimed_capacity -= capacity
        if request.claimed_capacity < 0:
            raise DSOLError("claimed more capacity than originally seized")
        if request.claimed_capacity == 0:
            self._processing.pop(requestor)
            self._stat_rtime.register(time - request.start_time)
        self._capacity += capacity
        self._stat_rutil.register(time, self._initial_capacity - self._capacity)
        # See if there is a waiter in the queue
        if self._queue.length() == 0:
            return
        first: ResourceRequest = self._waiting[self._queue.peek_first()]
        if self._capacity >= first.requested_capacity:
            self._queue.remove_first()
            self._allocate_capacity(first)
