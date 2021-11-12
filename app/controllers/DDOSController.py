import http.client
import time
import json
import joblib
from app.controllers.FeaturesController import FeaturesController
from app.controllers.SVMController import SVMController
from app.controllers.State import State
from app.model.ChartData import ChartData
from app.model.Flow import Flow

"""
    DDOSController class.
    This class 
"""


class DDOSController:
    def __init__(self, queue, period):
        self.queue = queue
        self.period = period
        self.svm_controller = SVMController()
        self.dpid = "1"
        self.legit_src_ips = []
        self.state = State.NORMAL
        self.normal_period = self.period
        self.anomalous_period = 21
        self.fc = FeaturesController(self.period)

    def run(self):
        current_period = self.normal_period
        self.read_flows()
        time.sleep(self.period)
        while True:
            if self.state == State.NORMAL:
                if current_period == self.normal_period:
                    print("NORMAL")

                    # Get all flows
                    conn = http.client.HTTPConnection("localhost", 8080)
                    conn.request("GET", "/stats/flow/1")
                    response = conn.getresponse()

                    # Read response
                    if response.status == 200:
                        flows_as_json = json.loads(response.read())
                        # print(json.dumps(flows_as_json, indent=4, sort_keys=True))
                    else:
                        flows_as_json = []

                    if len(flows_as_json) > 0:
                        # Clear variables
                        src_ips = []
                        dst_ips = []
                        n_packets_per_flow = []
                        bytes_per_flow = []
                        n_ip_flows = 0

                        flow_list = []

                        # Get flows info
                        for k in range(0, len(flows_as_json[self.dpid]) - 1):
                            if not (flows_as_json[self.dpid][k]["match"].get('nw_src') is None):
                                """src_ips.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                                dst_ips.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                                n_packets_per_flow.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                                bytes_per_flow.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                                n_ip_flows = n_ip_flows + 1
                                """
                                src_ip = flows_as_json[self.dpid][k]["match"]["nw_src"]
                                dst_ip = flows_as_json[self.dpid][k]["match"]["nw_dst"]
                                n_packets = flows_as_json[self.dpid][k]["packet_count"]
                                n_bytes = flows_as_json[self.dpid][k]["byte_count"]

                                # Append a new flow
                                flow_list.append(Flow(src_ip, dst_ip, n_packets, n_bytes))

                        # If there are flows based on src ip
                        if len(flow_list) > 0:
                            # Features controller
                            # fc = FeaturesController(src_ips=src_ips, dst_ips=dst_ips,
                            #                        n_packets_per_flow=n_packets_per_flow,
                            #                        bytes_per_flow=bytes_per_flow, n_flows=n_ip_flows,
                            #                        period=self.period)

                            self.fc.compute_period_flows(flow_list)


                            # Features object
                            f = self.fc.get_features()
                            # Get features
                            features = [f.get_ssip(), f.get_sdfp(), f.get_sdfb(), f.get_sfe(), f.get_rfip()]
                            print(features)
                            # Predict class
                            next_state = State(self.svm_controller.predict([features]))

                            # Update View
                            self.queue.put(ChartData(time.time(), f, next_state))

                            if next_state == State.ANOMALOUS:
                                self.__mitigate(flows_as_json=flows_as_json)
                            else:
                                self.__add_legit_src_ips(flows_as_json=flows_as_json)

                            self.state = next_state
                            current_period = 0

            elif self.state == State.ANOMALOUS:
                print("ANOMALOUS")
                if current_period == self.anomalous_period:
                    self.__del_drop_flow()
                    self.state = State.NORMAL
                    current_period = 0

            time.sleep(self.period)
            current_period += self.period


    def read_flows(self):
        # Get all flows
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("GET", "/stats/flow/1")
        response = conn.getresponse()

        # Read response
        if response.status == 200:
            flows_as_json = json.loads(response.read())
            # print(json.dumps(flows_as_json, indent=4, sort_keys=True))
        else:
            flows_as_json = []

        if len(flows_as_json) > 0:
            # Clear variables
            src_ips = []
            dst_ips = []
            n_packets_per_flow = []
            bytes_per_flow = []
            n_ip_flows = 0

            flow_list = []

            # Get flows info
            for k in range(0, len(flows_as_json[self.dpid]) - 1):
                if not (flows_as_json[self.dpid][k]["match"].get('nw_src') is None):
                    """src_ips.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                    dst_ips.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                    n_packets_per_flow.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                    bytes_per_flow.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                    n_ip_flows = n_ip_flows + 1
                    """
                    src_ip = flows_as_json[self.dpid][k]["match"]["nw_src"]
                    dst_ip = flows_as_json[self.dpid][k]["match"]["nw_dst"]
                    n_packets = flows_as_json[self.dpid][k]["packet_count"]
                    n_bytes = flows_as_json[self.dpid][k]["byte_count"]

                    # Append a new flow
                    flow_list.append(Flow(src_ip, dst_ip, n_packets, n_bytes))

            # If there are flows based on src ip
            if len(flow_list) > 0:
                # Features controller
                # fc = FeaturesController(src_ips=src_ips, dst_ips=dst_ips,
                #                        n_packets_per_flow=n_packets_per_flow,
                #                        bytes_per_flow=bytes_per_flow, n_flows=n_ip_flows,
                #                        period=self.period)

                self.fc.compute_period_flows(flow_list)


    def __del_drop_flow(self):
        drop_flow = json.dumps({
            "dpid": 1,
            "priority": 10,
            "match": {
                "ipv4_dst": "137.204.0.20",
                "dl_type": 2048,
            },
            # DROP
            "actions": []
        })
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("POST", "/stats/flowentry/delete_strict", drop_flow)

    def __add_legit_src_ips(self, flows_as_json):
        for k in range(0, len(flows_as_json[self.dpid]) - 1):
            if not (flows_as_json[self.dpid][k]["match"].get('nw_src') is None):
                src_ip = flows_as_json[self.dpid][k]["match"]["nw_src"]
                if src_ip not in self.legit_src_ips:
                    self.legit_src_ips.append(src_ip)

    def __mitigate(self, flows_as_json):
        # First delete all junk flow entries
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("DELETE", "/stats/flowentry/clear/1")

        # Then add a flow entry that drops all traffic with victim's destination IP
        drop_flow = json.dumps({
            "dpid": 1,
            "priority": 10,
            "match": {
                "ipv4_dst": "137.204.0.20",
                "dl_type": 2048,
            },
            # DROP
            "actions": []
        })
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("POST", "/stats/flowentry/add", drop_flow)

        packet_in_flow = json.dumps({
            "dpid": "1",
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
        for k in range(0, len(flows_as_json[self.dpid]) - 1):
            if not (flows_as_json[self.dpid][k]["match"].get('nw_src') is None):
                if flows_as_json[self.dpid][k]["match"]["nw_src"] in self.legit_src_ips and \
                        flows_as_json[self.dpid][k]["packet_count"] > 0:
                    action = flows_as_json[self.dpid][k]["actions"][0].split(":")
                    #print(flows_as_json[self.dpid][k]["match"]["nw_src"])
                    add_flow = json.dumps({
                        "dpid": self.dpid,
                        "priority": 20,
                        "match": {
                            "ipv4_src": flows_as_json[self.dpid][k]["match"]["nw_src"],
                            "ipv4_dst": flows_as_json[self.dpid][k]["match"]["nw_dst"],
                            "dl_type": flows_as_json[self.dpid][k]["match"]["dl_type"],
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
