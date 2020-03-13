import re
import math
from scipy.stats import nakagami
import matplotlib.pyplot as plt
import numpy as np
import random

POWER_TRANSMISSION =100
TRUNCATE_DISTANCE = 300 #If -1 it doesnt truncate at all

def decision(probability):
    return random.random() < probability

def getDistance(coord1, coord2):
    return math.sqrt((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)

class ConnectionManager():
    def __init__(self, veh):
        self.id = veh.id
        self.vehicle = veh
        self.simulator = veh.simulator
        self.connected_list = []
        self.curr_msg_buffer = []
        self.next_msg_buffer = []
        self.latest_control_msg_time = -1.0    # The last time when the vehicle receives a traffic control message
        self.latest_control_message = ""
        self.earliest_initialization_message = ""
        self.response_message_list = []
        self.position_message_list = []
        self.num_broadcast = {}

    def bind_simulator(self, sim):
        print("connection bind simulator")
        self.simulator = sim
        self.vehicle_list = self.simulator.vehicle_list

    def step(self):
        self.get_connected_list()
        self.curr_msg_buffer = self.next_msg_buffer
        self.next_msg_buffer = []

    def connected(self, vid):
        # check if the vehicle is connected (communicatable) to another vehicle (vid)
        # need to implement in the inherit class
        raise NotImplementedError

    def broadcast(self, msg):
        type_msg = msg["type_msg"]
        self.num_broadcast[type_msg] = self.num_broadcast.get(type_msg, 0) + 1
        for vid in self.connected_list:
            if vid in self.simulator.vehicle_list.keys():
                self.simulator.vehicle_list[vid].connection_manager.next_msg_buffer.append(msg)

    def get_connected_list(self):
        self.connected_list = []
        for vid in self.simulator.vehicle_list:
            if self.id != vid and self.connected(vid) == True:
                self.connected_list.append(vid)

    def classify_message(self):
        self.latest_control_message = ""
        self.earliest_initialization_message = ""
        earliest_selection_start_time = float(self.simulator.time)
        self.response_message_list = []
        self.position_message_list = []
        for msg in self.curr_msg_buffer:
            message_parsed = re.split(",", msg)
            if message_parsed[0] == "1":
                time = float(message_parsed[1])
                if time > self.latest_control_msg_time:
                    self.latest_control_msg_time = time
                    self.latest_control_message = msg
            elif message_parsed[0] == "2":
                time = float(message_parsed[1])
                if time < earliest_selection_start_time:
                    earliest_selection_start_time = time
                    self.earliest_initialization_message = msg
            elif message_parsed[0] == "3":
                self.response_message_list.append(msg)
            elif message_parsed[0] == "4":
                self.position_message_list.append(msg)

    def get_latest_control_message(self):   
        return self.latest_control_message

    def get_earliest_initialization_message(self):
        return self.earliest_initialization_message

    def get_response_message_list(self):
        return self.response_message_list

    def get_position_message_list(self):
        return self.position_message_list

    def get_num_broadcast(self):
        return self.num_broadcast

class DeterminedConnectionManager(ConnectionManager):
    # in this connection manager, the connection between vehicle is determined(non-probablistic) and 
    def __init__(self, veh):
        super(DeterminedConnectionManager, self).__init__(veh)


    def connected(self, vid):
        v = self.simulator.vehicle_list[vid]
        if self.vehicle.original_lane == v.original_lane:
            return True
        if self.vehicle.lane_position <= 30 and v.lane_position <= 30:
            return True
        return False

# Three types of connection: Ideal, Moderate and Harsh
class HarshConnectionManager(ConnectionManager):
    def __init__(self, veh):
        super(HarshConnectionManager,self).__init__(veh)

    def getProbability(self, x,psi):
        param = math.pow(x/psi,2)
        if TRUNCATE_DISTANCE >= 0 and x > TRUNCATE_DISTANCE:
            #print('truncate')
            return 0
        return math.exp(-param)


    def connected(self, vid):
       
        ownPosition = self.vehicle.position
        targetPosition = self.simulator.vehicle_list[vid].position
        distance = getDistance(ownPosition,targetPosition)
        
        #m = 1.0
        omega = POWER_TRANSMISSION
        proba = self.getProbability(distance,omega)
        #print("probability: ", proba)
        return decision(proba)
'''
class ModerateConnectionManager(ConnectionManager):
    def __init__(self, veh):
        super(ModerateConnectionManager,self).__init__(veh)

    def getProbability(self, x,psi):
        param = math.pow(x/psi,2)
        return math.exp(-2*param) * (1+2* param)

    def connected(self, vid):
        ownPosition = self.vehicle.position
        targetPosition = self.simulator.vehicle_list[vid].position
        distance = getDistance(ownPosition,targetPosition)
        
        #m=2.0
        omega=POWER_TRANSMISSION
        proba = self.getProbability(distance,omega)
        #print("probability: ", proba)
        return decision(proba)
'''
class IdealConnectionManager(ConnectionManager):
    def __init__(self, veh):
        super(IdealConnectionManager,self).__init__(veh)

    def getProbability(self, x,psi):
        param = math.pow(x/psi,2)
        if TRUNCATE_DISTANCE >= 0 and x > TRUNCATE_DISTANCE:
            #print('truncate')
            return 0
        return math.exp(-3*param) * (1+3* param + 9./2 * math.pow(param,2))


    def connected(self, vid):
        ownPosition = self.vehicle.position
        targetPosition = self.simulator.vehicle_list[vid].position
        distance = getDistance(ownPosition,targetPosition)
        
        #m=3.0
        omega=POWER_TRANSMISSION
        proba = self.getProbability(distance,omega)
        #print("probability: ", proba, distance, ownPosition, targetPosition)
        return decision(proba)

