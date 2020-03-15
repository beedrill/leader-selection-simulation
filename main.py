from simulator.simulator import Simulator 
from simulator.route_manager import DefaultRouteManager
from BapRuAlgorithmManager import BapRuAlgorithmManager as algo
# from algorithm import DummyAlgorithmManager as algo
from connection import DeterminedConnectionManager as determinedConn
from connection import IdealConnectionManager as idealConn
from connection import HarshConnectionManager as harshConn
rm = DefaultRouteManager("simulator/maps")
#algo = AlgorithmManager
connec = [determinedConn, idealConn, harshConn]
sim = Simulator(
    rm,  #route manager
    algo, #algorithm module
    connec[2],
    "simulator/maps", #map folder
    visual = False, # set to True if need to visually observe the simulation
    new_route = True # set to True if not need to re-generate vehicle routes
    )



rm.bind_simulator(sim)
sim.start_simulation()