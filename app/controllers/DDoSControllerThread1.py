import http.client
import time
import json
from datetime import datetime

from app.controllers.FeaturesController import FeaturesController
from app.controllers.SVMController import SVMController
from app.model.State import State
from app.model.Data import Data
from app.model.Flow import Flow
from app.model.TrafficState import TrafficState

"""
    DDOSController class.
"""

SAMPLING_PERIOD = 3
MITIGATION_PERIOD = 10
DPID = "1"
HIGH_PRIORITY = 20
MEDIUM_PRIORITY = 10
LOW_PRIORITY = 0
API_IP = "localhost"
API_PORT = "8080"


class DDoSControllerThread:
    def __init__(self, queue):
        self.queue = queue
        self.features_controller = None
        self.svm_controller = SVMController()
        self.legit_src_ips = []
        self.state = State.UNCERTAIN
        self.prec_state = State.UNCERTAIN
        self.most_targeted_ip = None
        self.f = None

    """
    Loop of DDoSControllerThread implemented using an Async FSM
    """
    def run(self):
        while True:
            if self.state == State.UNCERTAIN:
                """ Delete all flows, add Packet In flow and create new FeaturesController 
                in order to calculate features from scratch """
                if self.prec_state == State.UNCERTAIN or self.prec_state == State.ANOMALOUS:
                    self.del_flows_add_packet_in()
                    self.features_controller = FeaturesController(SAMPLING_PERIOD)
                self.prec_state = self.state

                # After waiting SAMPLING_PERIOD sec get flow entries
                time.sleep(SAMPLING_PERIOD)
                conn = http.client.HTTPConnection(API_IP, API_PORT)
                conn.request("GET", "/stats/flow/" + DPID)
                response = conn.getresponse()

                # Read response
                if response.status == 200:
                    sample_as_json = json.loads(response.read())
                else:
                    sample_as_json = []

                if len(sample_as_json) > 0:
                    # Read flow entries
                    sample = self.__read_sample(sample_as_json)
                    # If there are flows based on src ip
                    if len(sample) > 0:
                        # Get Features object
                        self.features_controller.add_sample(sample)
                        # Get most targeted IP in order to install a drop rule if the next state is ANOMALOUS
                        self.most_targeted_ip = self.features_controller.get_most_targeted_ip()

                        self.f = self.features_controller.get_features()
                        # Get features
                        features = [self.f.get_ssip(), self.f.get_sdfp(), self.f.get_sdfb(), self.f.get_sfe(),
                                    self.f.get_rfp()]

                        # Predict class
                        self.state = State(self.svm_controller.predict([features]).value)

            elif self.state == State.NORMAL:
                print("traffic is NORMAL")
                # Update View
                self.__update_view()
                # Add src ips as legitimate
                self.__add_legit_src_ips(sample_as_json)
                # Change state
                self.prec_state = self.state
                self.state = State.UNCERTAIN

            elif self.state == State.ANOMALOUS:
                print("traffic is ANOMALOUS")
                # Update View
                self.__update_view()
                # Mitigate attack
                print("mitigating attack: drop packets with destination IP " + self.most_targeted_ip)
                self.__mitigate(sample_as_json)
                time.sleep(MITIGATION_PERIOD)
                print("delete drop flow rule")
                self.prec_state = self.state
                self.state = State.UNCERTAIN
    
    """
    Delete all flow entries of DPID and add Packet In flow rule
    """
    
    def del_flows_add_packet_in(self):
        # Clear all flow entries
        conn = http.client.HTTPConnection(API_IP, API_PORT)
        conn.request("DELETE", "/stats/flowentry/clear/" + DPID)

        # Add packet in
        packet_in_flow = json.dumps({
            "dpid": DPID,
            "table_id": 0,
            "match": {},
            "priority": 0,
            "actions": [{
                "type": "OUTPUT",
                "port": "CONTROLLER"
            }]
        })
        conn = http.client.HTTPConnection(API_IP, API_PORT)
        conn.request("POST", "/stats/flowentry/add", packet_in_flow)

    """
    Read a Json with all the flow entries and store them into an array
    """

    def __read_sample(self, sample_as_json):
        # Sample array
        sample = []
        # Read flows from sample
        for k in range(0, len(sample_as_json[DPID]) - 1):
            if not (sample_as_json[DPID][k]["match"].get('nw_src') is None):
                src_ip = sample_as_json[DPID][k]["match"]["nw_src"]
                dst_ip = sample_as_json[DPID][k]["match"]["nw_dst"]
                packet_count = sample_as_json[DPID][k]["packet_count"]
                byte_count = sample_as_json[DPID][k]["byte_count"]
                # Append a new flow
                sample.append(Flow(src_ip, dst_ip, packet_count, byte_count))
        return sample

    """
    Update view method
    """
    def __update_view(self):
        time_string = datetime.now().strftime("%H:%M:%S")
        self.queue.put(
            Data(datetime.strptime(time_string, '%H:%M:%S'), self.f, TrafficState(self.state.value)))

    """
    This method adds legitimate source IPs (e.g. when the state is NORMAL) into
    an array in order to keep for them the connection up whenever an attack occurs
    """

    def __add_legit_src_ips(self, sample_as_json):
        for k in range(0, len(sample_as_json[DPID]) - 1):
            if not (sample_as_json[DPID][k]["match"].get('nw_src') is None):
                src_ip = sample_as_json[DPID][k]["match"]["nw_src"]
                packet_count = sample_as_json[DPID][k]["packet_count"]
                if src_ip not in self.legit_src_ips and packet_count > 0:
                    self.legit_src_ips.append(src_ip)

    """
    Perform mitigation: 
        1- Clear DPID of all the flow entries
        2- Add a flow rule which drops all the traffic sent to target host
        3- Add flow rules for legitimate source IPs in order to keep
            connection for them. 
    """
    def __mitigate(self, sample_as_json):
        conn = http.client.HTTPConnection(API_IP, API_PORT)
        conn.request("DELETE", "/stats/flowentry/clear/" + DPID)

        drop_flow = json.dumps({
            "dpid": DPID,
            "priority": MEDIUM_PRIORITY,
            "match": {
                "ipv4_dst": self.most_targeted_ip,
                "dl_type": 2048,
            },
            # DROP
            "actions": []
        })
        conn = http.client.HTTPConnection(API_IP, API_PORT)
        conn.request("POST", "/stats/flowentry/add", drop_flow)

        packet_in_flow = json.dumps({
            "dpid": DPID,
            "table_id": 0,
            "match": {},
            "priority": LOW_PRIORITY,
            "actions": [{
                "type": "OUTPUT",
                "port": "CONTROLLER"
            }]
        })
        conn = http.client.HTTPConnection(API_IP, API_PORT)
        conn.request("POST", "/stats/flowentry/add", packet_in_flow)

        # In conclusion keep connection for legitimate users
        for k in range(0, len(sample_as_json[DPID]) - 1):
            if not (sample_as_json[DPID][k]["match"].get('nw_src') is None):
                if sample_as_json[DPID][k]["match"]["nw_src"] in self.legit_src_ips and \
                        sample_as_json[DPID][k]["match"]["nw_dst"] == self.most_targeted_ip:
                    action = sample_as_json[DPID][k]["actions"][0].split(":")
                    #print(sample_as_json[DPID][k]["match"]["nw_src"])
                    add_flow = json.dumps({
                        "dpid": DPID,
                        "priority": HIGH_PRIORITY,
                        "match": {
                            "ipv4_src": sample_as_json[DPID][k]["match"]["nw_src"],
                            "ipv4_dst": sample_as_json[DPID][k]["match"]["nw_dst"],
                            "dl_type": sample_as_json[DPID][k]["match"]["dl_type"],
                        },
                        "actions": [
                            {
                                "type": action[0],
                                "port": action[1],
                            }
                        ]
                    })
                    conn = http.client.HTTPConnection(API_IP, API_PORT)
                    conn.request("POST", "/stats/flowentry/add", add_flow)
