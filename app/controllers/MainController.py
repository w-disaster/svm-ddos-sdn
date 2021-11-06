import http.client
import time
import json

from app.controllers.FeaturesController import FeaturesController
from app.model.Features import Features
from queue import Queue
import pandas as pd
import csv
import joblib
import threading

"""
    MainController class.
    This class 
"""
class MainController:
    def __init__(self, queue, period):
        self.queue = queue
        self.period = period

    def run(self):
        dpid = "1"
        filename = '../controllers/model.sav'
        loaded_model = joblib.load(filename)

        header = ["SSIP", "Stdevpack", "Stdevbyte", "NbFlow", "NbIntFlow"]
        normal_src_ips = []
        while True:
            conn = http.client.HTTPConnection("localhost", 8080)
            conn.request("GET", "/stats/flow/1")
            response = conn.getresponse()

            if response.status == 200:
                json_response = json.loads(response.read())
                #print(json.dumps(json_response, indent=4, sort_keys=True))
                # Read values from Json
                n_flows = len(json_response[dpid])
            else:
                n_flows = 0

            if n_flows > 0:
                src_ips = []
                dst_ips = []
                n_packets_per_flow = []
                bytes_per_flow = []
                n_ip_flows = 0

                for k in range(0, n_flows - 1):
                    if not (json_response[dpid][k]["match"].get('nw_src') is None):

                        src_ips.append(json_response[dpid][k]["match"]["nw_src"])
                        dst_ips.append(json_response[dpid][k]["match"]["nw_dst"])
                        n_packets_per_flow.append(json_response[dpid][k]["packet_count"])
                        bytes_per_flow.append(json_response[dpid][k]["byte_count"])
                        n_ip_flows = n_ip_flows + 1

                if n_ip_flows > 0:
                    # Features controller
                    fc = FeaturesController(src_ips=src_ips, dst_ips=dst_ips, n_packets_per_flow=n_packets_per_flow,
                                        bytes_per_flow=bytes_per_flow, n_flows=n_ip_flows, period=self.period)
                    # Features
                    features = fc.get_features()
                    # Write row into csv
                    row = [features.get_ssip(), features.get_sdfp(), features.get_sdfb(),
                           features.get_sfe(), features.get_rfip()]

                    # Update View
                    self.queue.put([("timestamp", time.time()), ("ssip", row[0]), ("sdfp", row[1]), ("sdfb", row[2]),
                                    ("sfe", row[3]), ("rfip", row[4])])

                    with open('live.csv', 'w') as datafile:
                        writer = csv.writer(datafile, delimiter=",")
                        writer.writerow(header)
                        writer.writerow(row)

                    dataset = pd.read_csv('live.csv').iloc[:].values
                    print(dataset)
                    result = loaded_model.predict(dataset)

                    if result[0] == 1:
                        print("ANOMALOUS")

                        # First delete all junk flow entries
                        conn = http.client.HTTPConnection("localhost", 8080)
                        conn.request("DELETE", "/stats/flowentry/clear/1")

                        # Then add a flow entry that drops all traffic with victim's destination IP
                        drop_flow = json.dumps({
                            "dpid": 1,
                            "match": {
                                "ipv4_dst": "192.168.1.20",
                                "dl_type": 2048,
                            },
                            # DROP
                            "actions": []
                        })
                        conn = http.client.HTTPConnection("localhost", 8080)
                        conn.request("POST", "/stats/flowentry/add", drop_flow)

                        # In conclusion keep connection for legitimate users
                        for k in range(0, n_flows - 1):
                            if not (json_response[dpid][k]["match"].get('nw_src') is None):
                                if json_response[dpid][k]["match"]["nw_src"] in normal_src_ips:
                                    action = json_response[dpid][k]["actions"][0].split(":")
                                    add_flow = json.dumps({
                                        "dpid": dpid,
                                        "priority": 10,
                                        "match": {
                                            "ipv4_src": json_response[dpid][k]["match"]["nw_src"],
                                            "ipv4_dst": json_response[dpid][k]["match"]["nw_dst"],
                                            "dl_type": json_response[dpid][k]["match"]["dl_type"],
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

                    else:
                        print("NORMAL")
                        for k in range(0, len(json_response[dpid]) - 1):
                            if not (json_response[dpid][k]["match"].get('nw_src') is None):
                                src_ip = json_response[dpid][k]["match"]["nw_src"]
                                if src_ip not in normal_src_ips:
                                    normal_src_ips.append(src_ip)

            time.sleep(self.period)
