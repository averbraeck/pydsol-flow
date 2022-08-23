"""
Test the resource classes (Queue and Resource).
""" 
import pytest
from pydsol.core.interfaces import SimulatorInterface, ReplicationInterface,\
    ModelInterface
from pydsol.core.simulator import DEVSSimulator
from pydsol.core.experiment import SingleReplication
from pydsol.core.model import DSOLModel


def test_queue_resource():

    class Model(DSOLModel):

        def __init__(self, simulator: SimulatorInterface):
            super().__init__(simulator)
            self.constructed = False
            self.count = 0
            
        def construct_model(self):
            self.constructed = True
            self.simulator.schedule_event_now(self, "inc")
            
        def inc(self):
            self.count += 1
            self.simulator.schedule_event_rel(10.0, self, "inc")

    simulator: DEVSSimulator = DEVSSimulator('sim', float, 0.0)
    model: ModelInterface = Model(simulator)
    replication: ReplicationInterface = SingleReplication(
        'rep', 0.0, 0.0, 100.0)
    try:
        assert not model.constructed
        simulator.initialize(model, replication)
        assert model.count == 0
        simulator.start()
        while simulator.is_starting_or_running():
            sleep(0.01)
        assert model.count == 11  # (0, 10, ..., 100)
        assert simulator.simulator_time == 100.0
        assert simulator.is_initialized()
        assert not simulator.is_starting_or_running()
        assert simulator.is_stopping_or_stopped()
        assert simulator.run_state == RunState.ENDED
        assert simulator.replication_state == ReplicationState.ENDED
        # cannot start simulator that has ended
        with pytest.raises(DSOLError):
            simulator.start()
        # cannot step simulator that has ended
        with pytest.raises(DSOLError):
            simulator.step()
        # cannot stop simulator that has ended
        with pytest.raises(DSOLError):
            simulator.stop()
    except Exception as e:
        raise e
    finally:
        simulator.cleanup()
