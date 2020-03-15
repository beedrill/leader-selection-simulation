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

# message type: traffic control message (1), selection initialization message (2), selection response message (3), lane position message (4)
# traffic control message: 1,<time of message>,<id of leader>
# selection initialization message: 2,<time of message>,<id of proposor>
# selection response message: 3,<id of proposer>,<id of acceptor>,<direction of acceptor>,<position of acceptor>
# lane position message: 4,<original lane>,<lane position>
class AlgorithmManager(object):
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.id = vehicle.id
        self.simulator = vehicle.simulator
        self.log = self.simulator.log
        self.connection_manager = vehicle.connection_manager
        self.leader = "-1"
        self.leader_time = 0                   # The time length after a vehicle becomes the leader
        self.is_group_leader = False
        self.is_prev_leader = False

        self.is_proposer = False               # Whether the vehicle is currently a proposer of a leader selection
        self.selection_time = 0                # The time lengtt after a leader selection is initialized
    def pre_step(self):
        #hook method to prepare algorithm status before the algorithm step 
        return 

    def post_step(self):
        #hook method to clean up after the algorithm step
        return

    def step(self):
        raise NotImplementedError

    def leave_intersection(self):
        #this method is called when the car leave the intersection
        return

    def is_leader(self):
        return self.leader == self.id

    def get_leader_switch_count(self):
        return 0

# message type: traffic control message (1)
# traffic control message: 1,<time of message>,<id of leader>

class ShenqiAlgorithmManager(AlgorithmManager):
    # this leader selection algorithm is designed and coded by Shenqi Zhang, so we use his name to name this algorithm class
    def __init__(self, vehicle):
        super(ShenqiAlgorithmManager, self).__init__(vehicle)
        self.is_group_leader = False
        self.silent_time = 0                   # The time length of no message received
        self.is_proposer = False               # Whether the vehicle is currently a proposer of a leader selection
        self.selection_time = 0                # The time lengtt after a leader selection is initialized

    def pre_step(self):
        self.vehicle.connection_manager.classify_message()
        self.vehicle.get_lane_position()

    def step(self):
        # Determine whether the vehicle is the group leader
        self.check_position_message()
        # broadcast lane position message
        position_message = "4," + self.vehicle.original_lane + "," + str(self.vehicle.lane_position)
        self.connection_manager.broadcast(position_message)

    def check_position_message(self):
        position_message_list = self.connection_manager.get_position_message_list()
        for msg in position_message_list:
            message_parsed = re.split(",", msg)
            if self.vehicle.original_lane == message_parsed[1] and self.vehicle.lane_position > float(message_parsed[2]):
                self.is_group_leader = False
                return
        self.is_group_leader = True

    def post_step(self):
        # If the vehicle is the leader
        if self.leader == self.id:
            self.leader_action()
        # If the vehicle is the group leader
        elif self.is_group_leader == True:
            self.group_leader_action()
        # If the vehicle is neither leader nor group leader, it only parses the most recent traffic control message
        else:
            self.non_leader_action()

    def leader_action(self):
        if self.leader_time == self.simulator.leader_time_threshold:
            successive_leader = self.leader_choose_successive_leader()
            print("successive_leader: " + successive_leader)
            # No matter whether the new leader exists or not, broadcast the result.
            control_message = str(1) + "," + str(self.simulator.time) + "," + successive_leader
            self.connection_manager.broadcast(control_message)
            self.is_prev_leader = True
            # If there is no successive leader, change the traffic light. Give itself the green light.
            if successive_leader == "-1":
                self.simulator.log.write(self.id + " no successive leader\n")
                #if self.vehicle.direction == "east-west":
                #    traci.trafficlight.setRedYellowGreenState("0", "rrrGGgrrrGGg")
                #elif self.vehicle.direction == "north-south":
                #    traci.trafficlight.setRedYellowGreenState("0", "GGgrrrGGgrrr")
            else:
                self.simulator.log.write(self.id + " select " + successive_leader + " as the successive leader\n")
        else:
            # Broadcast control message, tell others that itself is the leader
            control_message = str(1) + "," + str(self.simulator.time) + "," + str(self.id)
            self.connection_manager.broadcast(control_message)
            if self.leader_time == 0:
                pass
                # Give itself the red light
                #if self.vehicle.direction == "east-west":
                #    traci.trafficlight.setRedYellowGreenState("0", "GGgrrrGGgrrr")
                #elif self.vehicle.direction == "north-south":
                #    traci.trafficlight.setRedYellowGreenState("0", "rrrGGgrrrGGg")
            elif self.leader_time == self.simulator.leader_time_threshold - 2:
                # Initialize a new leader selection
                self.log.write(self.id + " initialize selection\n")
                initialization_message = str(2) + "," + str(self.simulator.time) + "," + str(self.id)
                self.connection_manager.broadcast(initialization_message)
        self.leader_time += 1

    def group_leader_action(self):
        self.group_leader_check_control_message()
        self.group_leader_check_initialization_message()
        # If the current leader selection is not aborted
        if self.is_proposer == True:
            self.selection_time += 1
            if self.selection_time == self.simulator.selection_time_threshold:
                new_leader = self.group_leader_choose_new_leader()
                self.leader = new_leader
                if new_leader != "-1":
                    print("new_leader: " + new_leader)
                    self.log.write(self.id + " choose " + new_leader + " as the new leader\n")
                    control_message = str(1) + "," + str(self.simulator.time) + "," + str(new_leader)
                    self.connection_manager.broadcast(control_message)
                self.silent_time = 0
                self.is_proposer = False
        else:
            if self.connection_manager.get_latest_control_message() == "" and self.connection_manager.get_earliest_initialization_message() == "":
                self.silent_time += 1
                # If the silent time is beyond the threshold, initialize a new leader selection.
                if self.silent_time == self.simulator.silent_time_threshold:
                    self.log.write(self.id + " initialize selection\n")
                    initialization_message = str(2) + "," + str(self.simulator.time) + "," + str(self.id)
                    self.connection_manager.broadcast(initialization_message)
                    self.is_proposer = True
                    self.selection_start_time = self.simulator.time
                    self.selection_time = 0
            else:
                self.silent_time = 0

    def non_leader_action(self):
        self.non_leader_check_control_message()
    
    # The current leader selects the successive leader
    def leader_choose_successive_leader(self):
        response_message_list = self.connection_manager.get_response_message_list()
        for msg in response_message_list:
            message_parsed = re.split(",", msg)
            if message_parsed[3] != self.vehicle.direction:
                return message_parsed[2]
        return "-1"

    # If there is a new control message, broadcast it and abort the leader selection initialized by itself.
    def group_leader_check_control_message(self):
        latest_control_message = self.connection_manager.get_latest_control_message()
        # If there is a new control message, broadcast it.
        if latest_control_message != "":
            message_parsed = re.split(",", latest_control_message)
            if self.leader != message_parsed[2]:
                self.log.write(self.id + " change the leader to " + message_parsed[2] + "\n")
            self.leader = message_parsed[2]
            self.is_proposer = False
            self.connection_manager.broadcast(latest_control_message)
            # If the vehicle becomes the new leader
            if self.leader == self.id:
                self.leader_time = 0

    # If there is an earlier leader selection, abort the leader selection initialized by itself.
    # If there is a concurrent leader selection and the id of the proposer is smaller, abort the leader selection initialized by itself.
    def group_leader_check_initialization_message(self):
        earliest_initialization_message = self.connection_manager.get_earliest_initialization_message()
        if earliest_initialization_message != "":
            message_parsed = re.split(",", earliest_initialization_message)
            time = float(message_parsed[1])
            vid = message_parsed[2]
            if self.is_proposer == True:
                if time < self.selection_start_time or (time == self.selection_start_time and int(vid) < int(self.id)):
                    self.is_proposer = False
            if self.is_proposer == False:
                self.log.write(self.id + " respond to " + vid + "\n")
                response_message = "3," + vid + "," + str(self.id) + "," + self.vehicle.direction + "," + str(self.vehicle.lane_position)
                self.connection_manager.broadcast(response_message)

    def group_leader_choose_new_leader(self):
        dict = {self.vehicle.direction: [self.id, self.vehicle.lane_position]}
        shortest_lane_position = self.vehicle.lane_position
        shortest_direction = self.vehicle.direction
        response_message_list = self.connection_manager.get_response_message_list()
        for msg in response_message_list:
            message_parsed = re.split(",", msg)
            if message_parsed[1] == self.id:
                id = message_parsed[2]
                direction = message_parsed[3]
                lane_position = float(message_parsed[4])
                if lane_position < shortest_lane_position:
                    shortest_lane_position = lane_position
                    shortest_direction = direction
                if direction in dict.keys():
                    if lane_position > dict[direction][1]:
                        dict[direction] = [id, lane_position]
                else:
                    dict[direction] = [id, lane_position]
        if len(dict) <= 1:
            return "-1"
        elif shortest_direction == "east-west":
            return dict["north-south"][0]
        else:
            return dict["east-west"][0]

    def non_leader_check_control_message(self):
        latest_control_message = self.connection_manager.get_latest_control_message()
        if latest_control_message != "":
            message_parsed = re.split(",", latest_control_message)
            if self.leader != message_parsed[2]:
                self.log.write(self.id + " change the leader to " + message_parsed[2] + "\n")
            self.leader = message_parsed[2]

class DummyAlgorithmManager():
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.id = vehicle.id
        self.simulator = vehicle.simulator
        self.log = self.simulator.log
        self.connection_manager = vehicle.connection_manager
        self.leader = "-1"
        self.leader_time = 0                   # The time length after a vehicle becomes the leader
        self.is_prev_leader = False
        self.is_group_leader = False
        self.silent_time = 0                   # The time length of no message received
        self.is_proposer = False               # Whether the vehicle is currently a proposer of a leader selection
        self.selection_time = 0                # The time lengtt after a leader selection is initialized

    def step(self):
        # Do nothing
        pass

    def action(self):
        # If the vehicle is the leader
        if self.leader == self.id:
            self.leader_action()
        # If the vehicle is not the leader
        else:
            self.non_leader_action()

    
    def leader_action(self):
        self.leader_check_control_message()
        # No matter whether itself is still the leader, broadcast the traffic control message.
        control_message = str(1) + "," + str(self.simulator.time) + "," + self.leader
        self.connection_manager.broadcast(control_message)

    def non_leader_action(self):
        self.non_leader_check_control_message()
        # If there is no new control message and the silent time is beyond the threshold, regard itself as the leader.
        if self.silent_time == self.simulator.silent_time_threshold:
            self.leader = self.id
            control_message = str(1) + "," + str(self.simulator.time) + "," + self.id
            self.connection_manager.broadcast(control_message)

    # If there is a new control message, regard other as the leader.
    def leader_check_control_message(self):
        latest_control_message = self.connection_manager.get_latest_control_message()
        if latest_control_message != "":
            message_parsed = re.split(",", latest_control_message)
            if self.leader != message_parsed[2]:
                self.log.write(self.id + " change the leader to " + message_parsed[2] + "\n")
                self.leader = message_parsed[2]

    # If there is a new control message, broadcast it.
    def non_leader_check_control_message(self):
        latest_control_message = self.connection_manager.get_latest_control_message()
        if latest_control_message != "":
            self.silent_time = 0
            message_parsed = re.split(",", latest_control_message)
            if self.leader != message_parsed[2]:
                self.log.write(self.id + " change the leader to " + message_parsed[2] + "\n")
                self.leader = message_parsed[2]
            self.connection_manager.broadcast(latest_control_message)
            # If the vehicle becomes the new leader
            if self.leader == self.id:
                self.leader_time = 0
        else:
            self.silent_time += 1

class BapAlgorithmManager(AlgorithmManager):
    
    def __init__(self, vehicle):
        super(BapAlgorithmManager, self).__init__(vehicle)
        self.leader = self.id
        self.counter = 0
        self.last_msg_received = self.create_leader_msg()
        self.last_received_leader_message_time = self.simulator.time
        self.silent_time = 0.4
        self.numSpam = 0

    def pre_step(self):

        return 

    def post_step(self):
        
        return

    def handle_leader_msg(self, msg):

        if msg["leader_id"] == self.id:
            return
        
        if self.leader != self.id \
        and msg["leader_id"] == self.leader \
        and msg["sequence_number"] > self.last_msg_received["sequence_number"]:
            self.last_msg_received = msg
            self.connection_manager.broadcast(msg)
            self.last_received_leader_message_time = self.simulator.time
        
            return
        
        if msg["leader_id"] != self.leader:
            needToChangeLeader = self.compare(msg)

            # in case the two potential leader are too close from one another
            if self.leader == self.id and abs(msg["lane_position"] - self.vehicle.lane_position) < 0.5:
                
                if self.numSpam >= 3:
                    self.numSpam = 0
                    needToChangeLeader =  msg["leader_id"] < self.last_msg_received["leader_id"]

                # count the number of time that situation happened
                if not needToChangeLeader:
                    self.numSpam += 1

            if needToChangeLeader:
                self.last_msg_received = msg
                self.last_received_leader_message_time = self.simulator.time
                self.leader = msg["leader_id"]
                self.connection_manager.broadcast(msg)


    
    # replace with the function you want
    # you may need to modify create leader msg if you want to have more information on the leader
    def compare(self, msg):
        return msg["lane_position"] < self.last_msg_received["lane_position"] 

    def create_leader_msg(self):
        # [message_type, car_id, distance to the center of the intersection, lane id, counter]
        return {
            "type_msg": "leader_msg", 
            "leader_id": self.id,
            "lane_position": self.vehicle.lane_position,
            "sequence_number": self.counter
        }

    def step(self):
        
        # if the car is his own leader
        if self.leader == self.id:
            self.last_msg_received = self.create_leader_msg()
            self.last_received_leader_message_time = self.simulator.time
            self.connection_manager.broadcast(self.last_msg_received)
            self.counter += 1
        
        for msg in self.connection_manager.curr_msg_buffer:
            if msg["type_msg"] == "leader_msg":
                self.handle_leader_msg(msg)

        # there is a timeout for receiving leader messages
        if abs(self.last_received_leader_message_time - self.simulator.time) > self.silent_time:
            self.last_msg_received = self.create_leader_msg()
            self.leader = self.last_msg_received["leader_id"]
