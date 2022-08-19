"""
pydsol_flow contains the base classes for flow-based discrete-event 
simulation.

Modules
-------
entities
    Entity classes that maintain their own statistics.
interfaces
    Common interfaces for classes to avoid circular references. The equivalent
    of the .h files in C++.
resources
    Resources and Queues that maintain their own statistics.
stations
    Standard stations such as the Generator, Server, and Sink.    

Dependencies
------------
pydsol_flow is only dependent on pydsol-core and standard Python libraries. 
For the unit tests, pytest is used, potentially with pytest-cov to assess 
the test coverage.
"""
