from simulator.simulator import Simulator 
from simulator.route_manager import DefaultRouteManager
from BapRuAlgorithmManager import BapRuAlgorithmManager as algo
# from algorithm import DummyAlgorithmManager as algo
from connection import DeterminedConnectionManager as determinedConn
from connection import IdealConnectionManager as idealConn
from connection import HarshConnectionManager as harshConn
connec = [determinedConn,idealConn, harshConn]
rm = DefaultRouteManager("simulator/maps")

number_simulation = 10

param = [True, False]
for k in range(len(param)):

    leader_msg_count = 0
    pos_msg_count = 0
    valid_time = 0
    avg_cvg_time = 0
    max_cvg_time = 0
    nbr_leader_changes = 0
    
    print("use param: ", param[k])
    algo.ACTIVATE_SWITCH = param[k]

    for i in range(number_simulation):
        print("================================================")
        print("simulation number: ", i)
        
        sim = Simulator(
            rm,  #route manager
            algo, #algorithm module
            connec[2],
            "simulator/maps", #map folder
            False
            )

        rm.bind_simulator(sim)
        sim.start_simulation()

        leader_msg_count += sim.get_count("leader_msg")
        pos_msg_count += sim.get_count("pos_msg")
        valid_time += sim.get_valid_time()
        avg_cvg_time += sim.get_avg_cvg_time()
        max_cvg_time += sim.get_max_cvg_time()
        nbr_leader_changes += sim.get_nbr_leader_changes()

    leader_msg_count /= number_simulation
    pos_msg_count /= number_simulation
    valid_time /= number_simulation
    avg_cvg_time /= number_simulation
    max_cvg_time /= number_simulation
    nbr_leader_changes /= number_simulation
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("result: ")
    print("nbr of leader messages: ", leader_msg_count)
    print("nbr of pos messages: ", pos_msg_count)
    print("% time with one leader", valid_time * 100)
    print("avg conv time: ", avg_cvg_time)
    print("max conv time: ", max_cvg_time)
    print("number of leader changes: ", nbr_leader_changes)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
