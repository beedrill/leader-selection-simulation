from simulator.simulator import Simulator 
from simulator.route_manager import DefaultRouteManager
from BapRuAlgorithmManager import BapRuAlgorithmManager as algo
# from algorithm import DummyAlgorithmManager as algo
from connection import DeterminedConnectionManager as determinedConn
from connection import IdealConnectionManager as idealConn
from connection import HarshConnectionManager as harshConn
#algo = AlgorithmManager
connec = [determinedConn,idealConn, harshConn]
rm = DefaultRouteManager("simulator/maps")

nbrSim = 10

param = [True, False]
for k in range(len(param)):

    leader_msg_count = 0
    pos_msg_count = 0
    validTime = 0
    avgCvgTime = 0
    maxCvgTime = 0
    nbrLeaderChanges = 0
    
    print("use param: ", param[k])
    algo.activate_switch = param[k]

    for i in range(nbrSim):

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

        leader_msg_count += sim.getCount("leader_msg")
        pos_msg_count += sim.getCount("pos_msg")
        validTime += sim.getValidTime()
        avgCvgTime += sim.getAvgCvgTime()
        maxCvgTime += sim.getMaxCvgTime()
        nbrLeaderChanges += sim.getNbrLeaderChanges()

    leader_msg_count /= nbrSim
    pos_msg_count /= nbrSim
    validTime /= nbrSim
    avgCvgTime /= nbrSim
    maxCvgTime /= nbrSim
    nbrLeaderChanges /= nbrSim

    print("result: ")
    print("nbr of leader messages: ", leader_msg_count);
    print("nbr of pos messages: ", pos_msg_count);
    print("% time with one leader", validTime * 100)
    print("avg conv time: ", avgCvgTime)
    print("max conv time: ", maxCvgTime)
    print("number of leader changes: ", nbrLeaderChanges)
