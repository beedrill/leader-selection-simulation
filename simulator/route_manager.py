# import xml.dom.minidom as minidom
import xml.etree.cElementTree as ET
import random 
import numpy as np

class RouteManager(object):
    def __init__(self, map_folder, 
    route_configs={
        "pattern":"fixed" #or "random"
        }):
        self.route_configs = route_configs

    def bind_simulator(self, sim):
        self.simulator = sim

    def init_routes(self):
        raise NotImplementedError

    def step(self):
        # print ("route manager stepped")
        return

class DefaultRouteManager(RouteManager):
    #Static array for random directions
    DIRECTIONS = ["west_in east_out", "north_in south_out", "east_in west_out", "south_in north_out"]

    def __init__(self, map_folder, 
        route_configs={
        "pattern":"fixed" #or "random"
        }):
        super(DefaultRouteManager, self).__init__(map_folder, route_configs = route_configs)

    def init_routes(self, is_traffic_dense, max_arrival_time = 240):
        if is_traffic_dense:
            beta = 1
        else:
            beta = 4
        exp = np.random.exponential(beta, 1000)
        next_depart = 0
        i = 0
        routes = ET.Element("routes")
        ET.SubElement(routes, "vType", accel="0.8", decel="4.5", id="car", length="5", maxSpeed="40", sigma="0.5")
        while next_depart <= max_arrival_time : 
            vehicle = ET.SubElement(routes, "vehicle" , color="1, 0, 0", depart= str(next_depart),  id= str(i),  type="car")
            ET.SubElement(vehicle, "route", edges = random.choice(DefaultRouteManager.DIRECTIONS))
            next_depart += exp[i]
            i += 1

        tree = ET.ElementTree(routes)
        tree.write('simulator/maps/map.rou.xml')