from simulator.simulator import Simulator 
from simulator.route_manager import DefaultRouteManager
from BapRuAlgorithmManager import BapRuAlgorithmManager as algo
from algorithm import BapAlgorithmManager as basic_algo
#from algorithm import DummyAlgorithmManager as algo
from connection import DeterminedConnectionManager as determinedConn
from connection import IdealConnectionManager as idealConn
from connection import HarshConnectionManager as harshConn
import argparse
import sys
map_dir = "simulator/maps"
parser = argparse.ArgumentParser(description='Simulation code for a proactive Leader selection algorithm in vehicular network')
parser.add_argument('--algorithm', default = 'advanced', help='specify algorithm, can be either basic or advanced, default is advanced; NOTE that basic algorithm will not adopt any optimization method, even if you specify in the commandline args')
parser.add_argument('--explicit_leader_switch', action='store_true', help='implement explicit leader switch')
parser.add_argument('--channel_condition', default = 'ideal', help='specify channel condition value can be either ideal or harsh')
parser.add_argument('--period_factor', default = '1', help='defined as the factor to multiply the original broadcast period when leader is converged, for example, if original broadcast period is 100ms,the period factor is 2 then after reaching convergence, the period factor will be 200ms)')
parser.add_argument('--heartbeat_factor', default = '2', help='heartbeat factor (if broadcast period is 100ms, heartbeat factor is 2, then the heartbeat detection will be 200ms)')
parser.add_argument('--optimize_backward_msg_propagation', action='store_true', help='use this to implement the optimization method that reduce the number of backward messages')
if __name__ == "__main__":

    cmd_args = parser.parse_args()

    ## specify algorithm:
    if cmd_args.algorithm == 'basic':
        algo = basic_algo
    elif cmd_args.algorithm != 'advanced':
        print ("unknown algorithm parameter... exiting.")
        sys.exit(1)

    ## car flow specification:
    rm = DefaultRouteManager( map_dir )

    ## explicit leader switch:
    algo.ACTIVATE_SWITCH = cmd_args.explicit_leader_switch

    ## heartbeat factor (if broadcast period is 100ms, heartbeat factor is 2, then the heartbeat detection will be 200ms):
    algo.HEARTBEAT_FACTOR = cmd_args.heartbeat_factor

    ## Period factor (defined as the factor to multiply the original broadcast period when leader is converged, for example, if original broadcast period is 100ms,
    #  the period factor is 2 then after reaching convergence, the period factor will be 200ms):
    algo.PERIOD_FACTOR = cmd_args.period_factor

    ## optimize backward messages:
    algo.REDUCE_BACKWARD_MESSAGE = cmd_args.optimize_backward_msg_propagation
  
    ## channel condition specification
    if cmd_args.channel_condition == 'ideal':
        connec = idealConn
    elif cmd_args.channel_condition == 'harsh':
        connec = harshConn
    else:
        print ("unknown channel condition parameter... exiting.")
        sys.exit(1)


    
    sim = Simulator(
        rm,  #route manager
        algo, #algorithm module
        connec,
        "simulator/maps", #map folder
        visual = False, # set to True if need to visually observe the simulation
        new_route = True # set to True if not need to re-generate vehicle routes
        )



    rm.bind_simulator(sim)
    sim.start_simulation()