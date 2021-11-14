import http.client
import time
import json
from datetime import datetime
from app.controllers.FeaturesControllerTraining import FeaturesControllerTraining
from app.controllers.SVMController import SVMController
from app.model.State import State
from app.model.Data import Data
from app.model.Flow import Flow

"""
    DDOSController class
"""

SAMPLING_PERIOD = 3
MITIGATION_PERIOD = 30
DPID = "1"
TARGET_HOST = "137.204.10.100"
HIGH_PRIORITY = 20
MEDIUM_PRIORITY = 10
LOW_PRIORITY = 0


class DDoSController:
    def __init__(self, queue):
        self.queue = queue
        self.svm_controller = SVMController()
        self.legit_src_ips = []
        self.state = State.UNCERTAIN
        self.f = []
        self.ff = []

    def run(self):
        while True:
            if self.state == State.UNCERTAIN:
                # Delete all flows, add Packet In flow, wait for SAMPLING_PERIOD
                self.del_flows_add_packet_in()
                time.sleep(SAMPLING_PERIOD)

                # Get all flows
                conn = http.client.HTTPConnection("localhost", 8080)
                conn.request("GET", "/stats/flow/1")
                response = conn.getresponse()

                # Read response
                if response.status == 200:
                    sample_as_json = json.loads(response.read())
                    #print(json.dumps(sample_as_json, indent=4, sort_keys=True))
                else:
                    sample_as_json = []

                # Read the sample if there's data in the response
                if len(sample_as_json) > 0:
                    sample = self.__read_sample(sample_as_json)
                    if len(sample) > 0:
                        # Features controller to calculate features from collected flows
                        fc = FeaturesControllerTraining(sample, TARGET_HOST, SAMPLING_PERIOD)

                        # Get features
                        self.f = fc.get_features().get_features_as_array()
                        features = [v for (k, v) in self.f]
                        print(features)

                        # Predict traffic state
                        self.state = State(self.svm_controller.predict([features]))

            elif self.state == State.NORMAL:
                print("NORMAL")

                # Update View
                self.queue.put(Data(datetime.now().strftime("%H:%M:%S"), self.ff, self.state))

                # Add src ips as legitimate
                self.__add_legit_src_ips(sample_as_json)
                # Change state
                self.state = State.UNCERTAIN

            elif self.state == State.ANOMALOUS:
                print("ANOMALOUS")

                # Update View
                self.queue.put(Data(datetime.now().strftime("%H:%M:%S"), self.ff, self.state))

                # Mitigate attack
                #self.__mitigate(sample_as_json)
                #time.sleep(SAMPLING_PERIOD)
                #self.__del_drop_flow()

                self.state = State.UNCERTAIN

    """
    Delete all flow entries of DPID and add Packet In flow rule
    """
    def del_flows_add_packet_in(self):
        # Clear all flow entries
        conn = http.client.HTTPConnection("localhost", 8080)
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
        conn = http.client.HTTPConnection("localhost", 8080)
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
                n_packets = sample_as_json[DPID][k]["packet_count"]
                n_bytes = sample_as_json[DPID][k]["byte_count"]
                # Append a new flow
                sample.append(Flow(src_ip, dst_ip, n_packets, n_bytes))
        return sample

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
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("DELETE", "/stats/flowentry/clear/" + DPID)

        drop_flow = json.dumps({
            "dpid": DPID,
            "priority": MEDIUM_PRIORITY,
            "match": {
                "ipv4_dst": TARGET_HOST,
                "dl_type": 2048,
            },
            # DROP
            "actions": []
        })
        conn = http.client.HTTPConnection("localhost", 8080)
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
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("POST", "/stats/flowentry/add", packet_in_flow)

        # In conclusion keep connection for legitimate users
        for k in range(0, len(sample_as_json[DPID]) - 1):
            if not (sample_as_json[DPID][k]["match"].get('nw_src') is None):
                if sample_as_json[DPID][k]["match"]["nw_src"] in self.legit_src_ips:
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
                    conn = http.client.HTTPConnection("localhost", 8080)
                    conn.request("POST", "/stats/flowentry/add", add_flow)
