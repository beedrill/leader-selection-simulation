import re
import csv
import xlwt
import xlrd
from xlutils.copy import copy
import math

try:
    import traci
except Exception:
    import os, sys
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
        import traci
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

class Simulator():
    def __init__(self, route_manager, algorithm_module, connection_module, map_folder, visual = True):
        self.map_folder = map_folder
        self.visual = visual
        self.algorithm_module = algorithm_module
        self.connection_module = connection_module
        if visual:
            self.sumo_binary = "sumo-gui"
        else:
            self.sumo_binary = "sumo"
        self.sumoCmd = [self.sumo_binary, "--step-length", "0.1", "-c", self.map_folder + "/traffic.sumocfg"]
        self.route_manager = route_manager
        self.time = 0
        self.vehicle_list = {}
        # Some constants
        self.silent_time_threshold = 2  # If a group leader experiences a certain time period without any message, it will start a leader selection.
        self.selection_time_threshold = 2  # The time length for a leader selection proposer to select messages
        self.leader_time_threshold = 200  # The time length for a leader. If the time is beyond the threshold, the leader will choose a new leader.
        # For the log file
        self.log = open("log.txt", "w")

        #for the stats
        csvfile_msg = open('stats/stats_msg.csv', 'w', newline='')
        self.csvwriter_msg = csv.writer(csvfile_msg, delimiter=',')

        csvfile_leader = open('stats/stats_leader.csv', 'w', newline='')
        self.csvwriter_leader = csv.writer(csvfile_leader, delimiter=',')

        csvfile_cvg = open('stats/stats_cvg.csv', 'w', newline='')
        self.csvwriter_cvg = csv.writer(csvfile_cvg, delimiter=',')

        self.num_msg_sent = {}
        self.num_msg_file = open("stats/num_msg.txt", "w")

        self.num_only_one_leader = 0
        self.num_valid_step = 0 # if there is at least on car a the center of the intersection
        self.only_one_leader_file = open("stats/only_one_leader.txt", "w")

        self.avg_convergence_time = 0
        self.max_convergence_time = 0
        self.cur_convergence_time = 0
        self.num_of_picks = 0
        self.pick_before = True
        self.last_count = 0
        self.max_convergence_time_file = open("stats/max_conv_time.txt", "w")

    def init_params(self):
        self.route_manager.init_routes(False)
        traci.start(self.sumoCmd)
        self.deltaT = traci.simulation.getDeltaT()

    def start_simulation(self):
        self.init_params()
        while traci.simulation.getMinExpectedNumber() > 0 and  traci.simulation.getTime() <= 200: 
            self.step()
            self.time += self.deltaT

        self.end_simulation()

    def get_count(self, type_msg):
        count = 0
        for key in self.num_msg_sent:
            count += self.num_msg_sent[key].get(type_msg, 0)
        return count

    def get_valid_time(self):
        if self.num_valid_step == 0:
            return math.inf
        return (self.num_only_one_leader / self.num_valid_step)
    
    def get_avg_cvg_time(self):
        if self.num_of_picks == 0:
            return math.inf
        return self.avg_convergence_time / self.num_of_picks

    def get_max_cvg_time(self):
        return self.max_convergence_time
    
    def get_nbr_leader_changes(self):
        return self.num_of_picks

    def end_simulation(self):
        traci.close()
        
        # FILE I/0 num_of_messages  
        # self.num_msg_file.write(str(count))
        # self.only_one_leader_file.write(str(self.num_only_one_leader / self.num_valid_step))
        # self.max_convergence_time_file.write(str(self.max_convergence_time))
        
        valid_time = self.get_valid_time()
        avg_cvg_time = self.get_avg_cvg_time()

        with open('excel/data_row_num.txt') as f:
            row_num = int(f.read())
            
        rb = xlrd.open_workbook('excel/data.xls')
        wb = copy(rb)
        w_sheet = wb.get_sheet(0)

        w_sheet.write(row_num, 0, self.get_count("leader_msg"))
        w_sheet.write(row_num, 1, self.get_count("pos_msg"))
        w_sheet.write(row_num, 2, valid_time)
        w_sheet.write(row_num, 3, avg_cvg_time)
        w_sheet.write(row_num, 4, self.max_convergence_time)
        w_sheet.write(row_num, 5, self.num_of_picks )
        wb.save('excel/data.xls')

        row_num += 1

        with open('excel/data_row_num.txt', 'w') as f:
            f.write(str(row_num))

        wb.save('excel/data.xls')
        
        print()
        print("nbr of leader messages: ", self.get_count("leader_msg"))
        print("nbr of pos messages: ", self.get_count("pos_msg"))
        print("% time with one leader", valid_time * 100)
        print("avg conv time: ", avg_cvg_time)
        print("max conv time: ", self.max_convergence_time)
        print("number of leader changes: ", self.num_of_picks)

    def step(self):
        traci.simulationStep()
        self.route_manager.step()
        self.maintain_vehicle_list()
        # Refresh parameters.
        for vid in self.vehicle_list:
            self.vehicle_list[vid].update_position()
            self.vehicle_list[vid].get_lane_position()
            self.vehicle_list[vid].connection_manager.step()
        for vid in self.vehicle_list:
            self.vehicle_list[vid].pre_step()
        for vid in self.vehicle_list:
            self.vehicle_list[vid].step()
        
        #self.print_vehicle()
        # Do actions
        for vid in self.vehicle_list:
            self.vehicle_list[vid].post_step()

        self.create_stats()


    # stats and useful color to distingish vehicle
    def create_stats(self):
        #count the number of leader at a given distance of the intersection center
        distance = 30
        number_of_leader = 0;
        number_of_car = 0
        for vid in self.vehicle_list:
            if self.vehicle_list[vid].lane_position < distance:
                number_of_car += 1
                if self.vehicle_list[vid].is_leader():
                    number_of_leader += 1

            if self.vehicle_list[vid].is_leader():
                # leader color
                traci.vehicle.setColor(vid, (255, 255, 255))
            else:
                # choose a color for the leader
                h = hash(self.vehicle_list[vid].get_leader() + 10*"padding")
                # take a bright color
                h0 = h % 128 + 128
                h1 = (h >> 8) % 128 + 128
                h2 = (h >> 16) % 128 + 128
                traci.vehicle.setColor(vid, (h0 , h1 , h2))
        
        count = self.get_count("leader_msg")

        self.csvwriter_msg.writerow([self.time, count - self.last_count]) #number_of_msg

        self.last_count = count

        self.csvwriter_leader.writerow([self.time, 1 if number_of_leader == 1 else 0]) #number_of_leader


        self.csvwriter_cvg.writerow([self.time, 0 if number_of_car >= 1 and number_of_leader != 1 else 1]) #number_of_leader


        #number of time there is only one leader
        if number_of_car >= 1:
            self.num_valid_step += 1
            if number_of_leader == 1:
                self.num_only_one_leader += 1

        #compute convergence time
        if number_of_car >= 1 and number_of_leader != 1:
            self.cur_convergence_time += self.deltaT
            self.pick_before = False 
        else:
            self.avg_convergence_time +=  self.cur_convergence_time
            self.max_convergence_time = max(self.max_convergence_time, self.cur_convergence_time)
            ## if no pick before...
            if not self.pick_before:
                self.num_of_picks += 1
                self.pick_before = True
            self.cur_convergence_time = 0
        
        for vid in self.vehicle_list:
            conn = self.vehicle_list[vid].connection_manager
            self.num_msg_sent[vid] = conn.get_num_broadcast()
        

    def maintain_vehicle_list(self):
        departed_id_list = traci.simulation.getDepartedIDList()
        for id in departed_id_list:
            if not id in self.vehicle_list.keys():
                self.vehicle_list[id] = Vehicle(id)
                v = self.vehicle_list[id]
                v.bind_simulator(self)
                v.bind_connection_manager(self.connection_module(v))
                v.bind_algorithm(self.algorithm_module(v))
        arrived_id_list = traci.simulation.getArrivedIDList()
        
        for id in arrived_id_list:
            if id in self.vehicle_list.keys():
                self.vehicle_list[id].leave_intersection()
                self.vehicle_list.pop(id)
                # color of the car out of the intersection
                traci.vehicle.setColor(id, (128, 0, 0))
        for id in list(self.vehicle_list):
            v = self.vehicle_list[id]
            if traci.vehicle.getLaneID(id) != v.original_lane:
                self.vehicle_list[id].leave_intersection()
                self.vehicle_list.pop(id)
                # color of the car out of the intersection
                traci.vehicle.setColor(id, (128, 0, 0))

    def print_vehicle(self):
        for _ in range(100):
            self.log.write("-")
        self.log.write("\n")
        self.log.write("time:" + str(self.time) + 
                       " traffic_light:" + traci.trafficlight.getRedYellowGreenState("0") + "\n")
        for vid in self.vehicle_list:
            v = self.vehicle_list[vid]
            self.log.write("vid:" + v.id + 
                           " original_lane:" + v.original_lane + 
                           " direction:" + v.direction + 
                           " lane_position:" + str(v.lane_position) + "\n")
            self.log.write("      connected_list:" + str(v.connection_manager.connected_list) + 
                           " curr_msg_buffer:" + str(v.connection_manager.curr_msg_buffer) + "\n")
            self.log.write("      leader:" + v.algorithm_manager.leader + 
                           " leader_time:" + str(v.algorithm_manager.leader_time) + "\n")
            self.log.write("      is_group_leader:" + str(v.algorithm_manager.is_group_leader) + 
                           " silent_time:" + str(v.algorithm_manager.silent_time) + 
                           " latest_control_msg_time:" + str(v.connection_manager.latest_control_msg_time) + "\n")
            self.log.write("      is_proposer:" + str(v.algorithm_manager.is_proposer) + 
                           " selection_time:" + str(v.algorithm_manager.selection_time) + "\n")
        for _ in range(100):
            self.log.write("-")
        self.log.write("\n")

class Vehicle():
    def __init__(self, id):
        self.id = id
        self.original_lane = traci.vehicle.getLaneID(self.id)
        self.direction = self.get_direction()
        self.lane_position = traci.lane.getLength(self.original_lane)
        self.position = traci.vehicle.getPosition(self.id)

    def bind_algorithm(self, algorithm_manager):
        self.algorithm_manager = algorithm_manager    

    def bind_connection_manager(self, connection_manager):
        self.connection_manager = connection_manager

    def bind_simulator(self, simulator):
        self.simulator = simulator

    def get_direction(self):
        list = re.split("_", self.original_lane)
        if list[0] == "east" or list[0] == "west":
            return "east-west"
        elif list[0] == "north" or list[0] == "south":
            return "north-south"

    def same_lane(self, veh):
        return self.original_lane == veh.original_lane

    def same_dir(self, veh):
        return self.direction == veh.direction


    #return distance toward the next intersection
    def get_lane_position(self): 
        from_origin = traci.vehicle.getLanePosition(self.id)  
        lane_length = traci.lane.getLength(self.original_lane)
        self.lane_position = lane_length - from_origin

    def update_position(self):
        self.position = traci.vehicle.getPosition(self.id)

    def pre_step(self):
        self.algorithm_manager.pre_step()

    def step(self): 
        self.algorithm_manager.step()

    def post_step(self):
        self.algorithm_manager.post_step()

    def leave_intersection(self):
        self.algorithm_manager.leave_intersection()

    def is_leader(self):
        return self.algorithm_manager.is_leader()

    def get_leader(self):
        return self.algorithm_manager.leader