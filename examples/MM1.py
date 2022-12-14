"""
"""

from pydsol.core.experiment import SingleReplication, Replication
from pydsol.core.interfaces import SimulatorInterface, ReplicationInterface
from pydsol.core.model import DSOLModel
from pydsol.core.pubsub import EventListener, Event
from pydsol.core.simulator import DEVSSimulatorFloat
from pydsol.core.statistics import Counter, Tally, WeightedTally, SimTally

from pydsol.flow.resources import Resource


class QueuingModel(DSOLModel):

    def __init__(self, simulator: SimulatorInterface):
        DSOLModel.__init__(self, simulator)
        
    def construct_model(self):
        self._res1: Resource = Resource("RES1", "Test resource 1",
                                        self._simulator, 1)
        sim: DEVSSimulatorFloat = self._simulator
        sim.schedule_event_abs(0.0, self, "arrival")
        
    def arrival(self):
        product = "object arriving at " + str(self._simulator.simulator_time)
        print("Generated: " + str(product))
        self._res1.seize(product, 1, self.seize_succeeded, entity=product)
        self._simulator.schedule_event_rel(4, self, "arrival")

    def seize_succeeded(self, entity):
        self._simulator.schedule_event_rel(5, self, "departure",
                                           entity=entity)
        
    def departure(self, entity):
        self._res1.release(entity, 1)
        

class MM1Simulation(EventListener):

    def __init__(self):
        self.simulator: DEVSSimulatorFloat = DEVSSimulatorFloat("sim")
        self.simulator.add_listener(ReplicationInterface.END_REPLICATION_EVENT, self)
        self.model: QueuingModel = QueuingModel(self.simulator)
        self.replication: Replication = SingleReplication("rep", 0.0, 0.0, 100.0)
        self.simulator.initialize(self.model, self.replication)
        self.simulator.start()

    def notify(self, event: Event):
        if event.event_type == ReplicationInterface.END_REPLICATION_EVENT:
            self.report()
    
    def report(self):
        """ Loop through the statistics and print all. """ 
        print("\n\nEnd simulation\n")

        print(Counter.report_header())
        for stat in self.model.output_statistics().values():
            if isinstance(stat, Counter):
                print(stat.report_line())
        print(Counter.report_footer())
        print()

        print(Tally.report_header())
        for stat in self.model.output_statistics().values():
            if isinstance(stat, Tally):
                print(stat.report_line())
        print(Tally.report_footer())
        print()

        print(WeightedTally.report_header())
        for stat in self.model.output_statistics().values():
            if isinstance(stat, WeightedTally):
                print(stat.report_line())
        print(WeightedTally.report_footer())


if __name__ == "__main__":
    MM1Simulation()
    
