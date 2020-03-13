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
import re

from algorithm import AlgorithmManager
import math


# todo name the constants properly
class BapRuAlgorithmManager(AlgorithmManager):

    # static variable
    ACTIVATE_SWITCH = True
    PERIOD_FACTOR = 1 # when the agent is not receiving conflict leader messages, then it set the period to a lower frequency
    # e.g., if original period is 100ms and PERIOD_FACTOR = 1.5, then the broadcast period after convergence will be 150ms

    
    def __init__(self, vehicle):
        super(BapRuAlgorithmManager, self).__init__(vehicle)
        
        self.counter = 0
        self.last_received_leader_message_time = self.simulator.time
        self.num_spam = 0
        self.max_spam_number = 3
        self.threshold_dec_freq_msg = 5

        self.max_dis_switch_leader = 30
        self.max_leader_force_time = 3

        self.init_leader()
        
    def pre_step(self):
        return 

    def post_step(self):
        return

    def init_leader(self, pos_vehicles = {}, force_time = 0):
        self.leader = self.id
        self.last_lead_msg_sent = 0
        self.time_leader = 0
        self.lead_msg_dt = 0.1
        self.last_msg_received = self.create_leader_msg()
        self.dis_to_leader = 0

        self.pos_vehicles = pos_vehicles
        self.force_time = force_time

    # when a car follow a leader, then it must addapt his silent 
    # time according to the lead msg freq
    def silentTime(self):
        return self.last_msg_received["lead_msg_dt"] * 3


    def handle_leader_msg(self, msg):

        if msg["leader_id"] == self.id and self.is_leader():
            return

        if msg["leader_id"] != self.leader:
            need_to_change_leader = self.selfCompare(msg)

            # in case two car can't decide to be a leader
            # this condition is not probable in real life
            if self.is_leader() and abs(msg["lane_position"] - self.vehicle.lane_position) < 0.5:
                if self.num_spam >= self.max_spam_number:
                    self.num_spam = 0
                    need_to_change_leader =  msg["leader_id"] < self.last_msg_received["leader_id"]

                if not need_to_change_leader:
                    self.num_spam += 1

            if msg["force_leader"]:
                need_to_change_leader = True
            
            # this is the only place we can change the leader
            if need_to_change_leader:
                self.leader = msg["leader_id"]
                self.last_received_leader_message_time = self.simulator.time
                self.last_msg_received = msg

            return
        
        if not self.is_leader() \
        and msg["leader_id"] == self.leader:

            # decide if the message have to be relayed
            if msg["sequence_number"] > self.last_msg_received["sequence_number"]:

                if(not self.neighbors().issubset(self.last_msg_received["visited"])):
                    # broadcast the message
                    self.add_neighbors_to_visited()
                    self.connection_manager.broadcast(self.last_msg_received)
                
                self.dis_to_leader = min(msg["dis_to_leader"] + 1, self.dis_to_leader)
                self.last_received_leader_message_time = self.simulator.time
                self.last_msg_received = msg
            else:
                self.add_new_visited(msg)
                self.dis_to_leader = msg["dis_to_leader"] + 1

    # replace with the function you want
    # you may need to modify create leader msg if you want to have more information on the leader
    def selfCompare(self, msg):
        return self.compare(msg, self.last_msg_received)

    # replace with the function you want
    # you may need to modify create leader msg if you want to have more information on the leader
    def compare(self, msg1, msg2):
        return msg1["lane_position"] < msg2["lane_position"] 

    def neighbors(self):
        return set(self.connection_manager.connected_list)

    def create_leader_msg(self):
        # [message_type, leader id, distance to intersecrion center, set of visited car,
        # id of leader message, frequence between lead messages,
        # dis from the leader in leader graph, force the leader to stay leader]
        return {
            "type_msg": "leader_msg", 
            "leader_id": self.id,
            "lane_position": self.vehicle.lane_position,
            "visited": set(self.connection_manager.connected_list),
            "sequence_number": self.counter,
            "lead_msg_dt": self.lead_msg_dt,
            "dis_to_leader": 0,
            "force_leader": False
        }

    # the 2 next function are used to change the set of visited car in leader message

    def add_new_visited(self, msg):
        self.last_msg_received["visited"] = msg["visited"].union(self.last_msg_received["visited"])

    def add_neighbors_to_visited(self):
        self.last_msg_received["visited"] = self.neighbors().union(self.last_msg_received["visited"])
        self.last_msg_received["dis_to_leader"] += 1

    # handle position messages
    def handle_pos_msg(self, msg):
        if msg["leader_id"] != self.leader:
            return 

        if self.is_leader():
            # record the pos of all car
            self.pos_vehicles[msg["vehicle_id"]] = msg

        # relay it only if the car which received is closer to the leader
        elif msg["dis_to_leader"] < self.dis_to_leader:
            msg["dis_to_leader"] = self.dis_to_leader
            self.connection_manager.broadcast(msg)

    # postion messages
    def create_pos_msg(self):
        # [type message, vehicle id, leader id, distance from the center, original lane
        #, dis to leader in position message graph, direction, time message sent]
        return {
            "type_msg": "pos_msg",
            "vehicle_id": self.id,
            "leader_id": self.leader,
            "lane_position": self.vehicle.lane_position,
            "original_lane": self.vehicle.original_lane,
            "dis_to_leader": self.dis_to_leader,
            "direction": self.vehicle.get_direction(),
            "time": self.simulator.time
        }

    def leader_step(self):
        self.time_leader += self.simulator.deltaT

        if self.last_lead_msg_sent < self.lead_msg_dt:
            
            # we do this every time, it works better than only one time
            if self.time_leader >= self.threshold_dec_freq_msg:
                #change the frequency and send the new silent_time
                self.lead_msg_dt = BapRuAlgorithmManager.PERIOD_FACTOR * self.lead_msg_dt
                


            self.last_msg_received = self.create_leader_msg()

            #force him to be the leader
            if self.time_leader < self.force_time:
                self.last_msg_received["lane_position"] = 0


            self.last_received_leader_message_time = self.simulator.time
            self.connection_manager.broadcast(self.last_msg_received)
            self.counter += 1
            self.last_lead_msg_sent = 0
        else:
            self.last_lead_msg_sent += self.simulator.deltaT
        
        self.pos_vehicles[self.id] = self.create_pos_msg()

    def step(self):

        for msg in self.connection_manager.curr_msg_buffer:
            # todo change force leader
            if msg["type_msg"] == "leader_msg" and msg["force_leader"] and msg["leader_id"] == self.id:
                self.init_leader(msg["pos_vehicles"], self.max_leader_force_time)
                break
        
        # if the car is his own leader
        if self.is_leader():
            self.leader_step()
        else:
            self.connection_manager.broadcast(self.create_pos_msg())
        
        for msg in self.connection_manager.curr_msg_buffer:
            if msg["type_msg"] == "leader_msg":
                self.handle_leader_msg(msg)

            if msg["type_msg"] == "pos_msg":
                self.handle_pos_msg(msg)

        # there is a timeout for receiving leader messages
        if not self.is_leader() \
        and abs(self.last_received_leader_message_time - self.simulator.time) > self.silentTime():
            # become a leader
            self.init_leader()

    def create_next_leader_msg(self, next_leader):
        # [message_type, leader id, distance to intersecrion center, set of visited car,
        # id of leader message, frequence between lead messages,
        # dis from the leader in leader graph, force the leader to stay leader]
        return {
            "type_msg": "leader_msg", 
            "leader_id": next_leader,
            "lane_position": 0,
            "visited": set(self.connection_manager.connected_list), # todo what should we put here
            "sequence_number": self.counter,
            "lead_msg_dt": self.lead_msg_dt,
            "dis_to_leader": 0,
            "force_leader": True,
            "pos_vehicles": self.pos_vehicles
        }

    # get the closest on the given lane
    def get_next_leader_on_lane(self, pred):
        best_msg_pos = None

        for id_car, pos_msg in self.pos_vehicles.items():

            # the car is not on the i,tersection anymore
            if abs(self.simulator.time - pos_msg["time"]) > 1:
                continue
            
            # take the best on a different lane
            if id_car != self.id  and pos_msg["lane_position"] < self.max_dis_switch_leader \
                and pred(best_msg_pos, pos_msg):
                best_msg_pos = pos_msg

        return None if best_msg_pos is None else best_msg_pos["vehicle_id"]

    # to select the next leader:
    # - we take the closest car in a different direction (n-s or e-w) in a 30m radius
    # - if there is none, then take the farthest car on the same direction (deacrese leader switch number)
    def get_next_leader(self):
        
        farthest_same_dir = \
            lambda best_msg, msg: msg["direction"] == self.vehicle.direction \
            and (best_msg is None or msg["lane_position"] > best_msg["lane_position"])

        closest_diff_dir = \
            lambda best_msg, msg: msg["direction"] != self.vehicle.direction \
            and (best_msg is None or msg["lane_position"] < best_msg["lane_position"])

        new_leader = self.get_next_leader_on_lane(closest_diff_dir)
        if not new_leader is None:
            return new_leader
        return self.get_next_leader_on_lane(farthest_same_dir)
        

    #this method is called when the car leave the intersection
    def leave_intersection(self):

        if not self.is_leader():
            return

        new_leader = self.get_next_leader()

        if new_leader is None:
            return

        msg = self.create_next_leader_msg(new_leader)
        if BapRuAlgorithmManager.ACTIVATE_SWITCH:
            self.connection_manager.broadcast(msg)