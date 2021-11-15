import http.client
import time
import json
from app.controllers.FeaturesController import FeaturesController
from app.controllers.SVMController import SVMController
from app.model.State import State
from app.model.Data import ChartData
from app.model.Flow import Flow

"""
    DDOSController class.
"""
SAMPLING_PERIOD = 3
MITIGATION_PERIOD = 60
DPID = "1"
TARGET_HOST = "137.204.60.10"


class DDOSController:
    def __init__(self, queue):
        self.queue = queue
        self.svm_controller = SVMController()
        self.legit_src_ips = []
        self.state = State.NOT_DETERMINED
        self.fc = FeaturesController(SAMPLING_PERIOD, TARGET_HOST)
        self.f = []
        self.flag = False

    def run(self):
        while True:
            if self.state == State.NOT_DETERMINED:
                # Get all flows
                conn = http.client.HTTPConnection("localhost", 8080)
                conn.request("GET", "/stats/flow/1")
                response = conn.getresponse()

                # Read response
                if response.status == 200:
                    sample_as_json = json.loads(response.read())
                    # print(json.dumps(sample_as_json, indent=4, sort_keys=True))
                else:
                    sample_as_json = []

                if len(sample_as_json) > 0:
                    # Read flow entries
                    sample = self.__read_sample(sample_as_json)
                    # If there are flows based on src ip
                    if len(sample) > 0:
                        # Add sample
                        self.fc.add_sample(sample, self.flag)
                        if self.fc.is_first_sample_set():
                            # Get Features object
                            self.f = self.fc.get_features()
                            # Get features
                            features = [self.f.get_ssip(), self.f.get_sdfp(), self.f.get_sdfb(), self.f.get_sfe(),
                                        self.f.get_rfip()]
                            print(features)
                            # Predict class
                            self.state = State(self.svm_controller.predict([features]))
                        else:
                            time.sleep(SAMPLING_PERIOD)
                        if self.flag:
                            self.flag = False
                    else:
                        time.sleep(MITIGATION_PERIOD)

            elif self.state == State.NORMAL:
                print("NORMAL")
                # Update View
                self.queue.put(ChartData(time.time(), self.f, self.state))
                # Add src ips as legitimate
                self.__add_legit_src_ips(sample_as_json)
                time.sleep(SAMPLING_PERIOD)
                self.state = State.NOT_DETERMINED

            elif self.state == State.ANOMALOUS:
                print("ANOMALOUS")
                # Update View
                self.queue.put(ChartData(time.time(), self.f, self.state))
                # Mitigate attack
                self.__mitigate(sample_as_json)
                time.sleep(30000)
                #time.sleep(MITIGATION_PERIOD)
                self.__del_drop_flow()
                self.fc.clear_fields()
                time.sleep(SAMPLING_PERIOD)
                self.flag = True
                # self.fc = FeaturesController(SAMPLING_PERIOD, TARGET_HOST)
                self.state = State.NOT_DETERMINED

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

    def __add_legit_src_ips(self, sample_as_json):
        for k in range(0, len(sample_as_json[DPID]) - 1):
            if not (sample_as_json[DPID][k]["match"].get('nw_src') is None):
                src_ip = sample_as_json[DPID][k]["match"]["nw_src"]
                packet_count = sample_as_json[DPID][k]["packet_count"]
                if src_ip not in self.legit_src_ips and packet_count > 0:
                    self.legit_src_ips.append(src_ip)

    def __mitigate(self, sample_as_json):
        # First delete all junk flow entries

        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("DELETE", "/stats/flowentry/clear/" + DPID)
        print(conn.getresponse().status)

        # Then add a flow entry that drops all traffic with victim's destination IP
        drop_flow = json.dumps({
            "dpid": DPID,
            "priority": 10,
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
            "priority": 0,
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
                if sample_as_json[DPID][k]["match"]["nw_src"] in self.legit_src_ips and \
                        sample_as_json[DPID][k]["packet_count"] > 0:
                    action = sample_as_json[DPID][k]["actions"][0].split(":")
                    # print(sample_as_json[DPID][k]["match"]["nw_src"])
                    add_flow = json.dumps({
                        "dpid": DPID,
                        "priority": 20,
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

    def __del_drop_flow(self):
        """drop_flow = json.dumps({
            "dpid": DPID,
            "priority": 10,
            "match": {
                "ipv4_dst": TARGET_HOST,
                "dl_type": 2048,
            },
            # DROP
            "actions": []
        })
        conn =http.client.HTTPConnection("localhost", 8080)
        conn.request("POST", "/stats/flowentry/delete_strict", drop_flow)
        """
        # First delete all junk flow entries
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("DELETE", "/stats/flowentry/clear/1")

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
