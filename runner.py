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
parser.add_argument('--stable_period', default = 0.1, type =float, help='period when leader is converged')
parser.add_argument('--car_flow', default = 0.25, type =float, help='period when leader is converged')
parser.add_argument('--heartbeat_factor', default = 2, type = float, help='heartbeat factor (if broadcast period is 100ms, heartbeat factor is 2, then the heartbeat detection will be 200ms)')
parser.add_argument('--optimize_backward_msg_propagation', action='store_true', help='use this to implement the optimization method that reduce the number of backward messages')
parser.add_argument('--saving_file_name', default = None, type = str, help='specify the file name to save the results')
parser.add_argument('--trials', default = 1, type = int, help='how many trials to do and get results as average')
if __name__ == "__main__":

    cmd_args = parser.parse_args()

    ## specify algorithm:
    if cmd_args.algorithm == 'basic':
        algo = basic_algo
    elif cmd_args.algorithm != 'advanced':
        print ("unknown algorithm parameter... exiting.")
        sys.exit(1)

    ## car flow specification:
    rm = DefaultRouteManager( map_dir, car_flow = cmd_args.car_flow )

    ## explicit leader switch:
    algo.ACTIVATE_SWITCH = cmd_args.explicit_leader_switch

    ## heartbeat factor (if broadcast period is 100ms, heartbeat factor is 2, then the heartbeat detection will be 200ms):
    algo.HEARTBEAT_FACTOR = cmd_args.heartbeat_factor

    ## Period factor (defined as the factor to multiply the original broadcast period when leader is converged, for example, if original broadcast period is 100ms,
    #  the period factor is 2 then after reaching convergence, the period factor will be 200ms):
    algo.PERIOD_LEADER_STABLE = cmd_args.stable_period

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


    total_num_leader_msg = 0
    total_orig_num_leader_msg = 0
    total_num_pos_msg = 0
    total_valid_time = 0
    total_avg_cvg_time = 0
    total_max_cvg_time = 0
    total_num_leader_changes = 0

    
    for _ in range(cmd_args.trials):
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

        num_leader_msg = sim.get_count("leader_msg")
        num_orig_leader_msg = sim.get_count("original_leader_msg")
        num_pos_msg = sim.get_count("pos_msg")
        valid_time = sim.get_valid_time()
        avg_cvg_time = sim.get_avg_cvg_time()
        max_cvg_time = sim.get_max_cvg_time()
        num_leader_changes = sim.get_nbr_leader_changes()

        print()
        print("nbr of leader messages: ", num_leader_msg)
        print("nbr of original leader messages: ", num_orig_leader_msg)
        print("nbr of pos messages: ", num_pos_msg)
        print("% time with one leader", valid_time*100)
        print("avg conv time: ", avg_cvg_time)
        print("max conv time: ", max_cvg_time)
        print("number of leader changes: ", num_leader_changes)

        total_num_leader_msg += sim.get_count("leader_msg")
        total_orig_num_leader_msg += sim.get_count("original_leader_msg")
        total_num_pos_msg += sim.get_count("pos_msg")
        total_valid_time += sim.get_valid_time()
        total_avg_cvg_time += sim.get_avg_cvg_time()
        total_max_cvg_time += sim.get_max_cvg_time()
        total_num_leader_changes += sim.get_nbr_leader_changes()

    if cmd_args.saving_file_name:
        print ('writing to file: stats/'+cmd_args.saving_file_name)
        f = open('stats/'+cmd_args.saving_file_name, 'a')
        f.write('{}, {}, {}, {}, {}, {}, {}\n'.format(
            total_num_leader_msg/cmd_args.trials, #number of leader messages
            total_orig_num_leader_msg/cmd_args.trials, #number of leader messages sent by leaders only
            total_num_pos_msg/cmd_args.trials, # number of position messages (messages sending back to leader)
            total_valid_time/cmd_args.trials, # valid time percentage of the time having 1 leader
            total_avg_cvg_time/cmd_args.trials, # average convergence time
            total_max_cvg_time/cmd_args.trials, # maximum convergence time
            total_num_leader_changes/cmd_args.trials # number of times leader changes
        ))
        f.close()