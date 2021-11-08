import http.client
import time
import json
import joblib
from app.controllers.FeaturesController import FeaturesController
from app.controllers.SVMController import SVMController, Traffic
from app.model.ChartData import ChartData

"""
    MainController class.
    This class 
"""


class MainController:
    def __init__(self, queue, period):
        self.queue = queue
        self.period = period
        self.svm_controller = SVMController()
        self.dpid = "1"
        self.legit_src_ips = []

    def run(self):
        while True:
            # Get all flows
            conn = http.client.HTTPConnection("localhost", 8080)
            conn.request("GET", "/stats/flow/1")
            response = conn.getresponse()

            # Read response
            if response.status == 200:
                flows_as_json = json.loads(response.read())
                #print(json.dumps(flows_as_json, indent=4, sort_keys=True))
            else:
                flows_as_json = []

            if len(flows_as_json) > 0:
                # Clear variables
                src_ips = []
                dst_ips = []
                n_packets_per_flow = []
                bytes_per_flow = []
                n_ip_flows = 0

                # Get flows info
                for k in range(0, len(flows_as_json[self.dpid]) - 1):
                    if not (flows_as_json[self.dpid][k]["match"].get('nw_src') is None):
                        src_ips.append(flows_as_json[self.dpid][k]["match"]["nw_src"])
                        dst_ips.append(flows_as_json[self.dpid][k]["match"]["nw_dst"])
                        n_packets_per_flow.append(flows_as_json[self.dpid][k]["packet_count"])
                        bytes_per_flow.append(flows_as_json[self.dpid][k]["byte_count"])
                        n_ip_flows = n_ip_flows + 1

                # If there are flows based on src ip
                if n_ip_flows > 0:
                    # Features controller
                    fc = FeaturesController(src_ips=src_ips, dst_ips=dst_ips, n_packets_per_flow=n_packets_per_flow,
                                        bytes_per_flow=bytes_per_flow, n_flows=n_ip_flows, period=self.period)

                    # Features object
                    f = fc.get_features()
                    # Get features
                    features = [f.get_ssip(), f.get_sdfp(), f.get_sdfb(), f.get_sfe(), f.get_rfip()]
                    print(features)
                    # Predict class
                    traffic = self.svm_controller.predict([features])

                    # Update View
                    self.queue.put(ChartData(time.time(), f, traffic))

                    # Mitigate if anomalous, add legit src ips otherwise
                    if traffic == Traffic.ANOMALOUS:
                        print("ANOMALOUS")
                        self.__mitigate(flows_as_json=flows_as_json)
                        time.sleep(20)

                    else:
                        print("NORMAL")
                        self.__add_legit_src_ips(flows_as_json=flows_as_json)

            time.sleep(self.period)

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
            "match": {
                "ipv4_dst": "137.204.0.20",
                "dl_type": 2048,
            },
            # DROP
            "actions": []
        })
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("POST", "/stats/flowentry/add", drop_flow)

        # In conclusion keep connection for legitimate users
        for k in range(0, len(flows_as_json[self.dpid]) - 1):
            if not (flows_as_json[self.dpid][k]["match"].get('nw_src') is None):
                if flows_as_json[self.dpid][k]["match"]["nw_src"] in self.legit_src_ips:
                    action = flows_as_json[self.dpid][k]["actions"][0].split(":")
                    add_flow = json.dumps({
                        "dpid": self.dpid,
                        "priority": 10,
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
