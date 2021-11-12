#!/usr/bin/python3
import csv
import http
import json
import time

from app.controllers.FeaturesControllerTraining import FeaturesControllerTraining
from app.model.Flow import Flow

# Variables
MAX_SAMPLES = 500
PERIOD = 3
DPID = "1"
f = open('dataset3.csv', 'w')
writer = csv.writer(f)


def build_dataset():
    # Collect MAX_SAMPLES samples
    for i in range(1, MAX_SAMPLES):
        # Get all flows
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("GET", "/stats/flow/1")
        response = conn.getresponse()

        # Read response
        if response.status == 200:
            flows_as_json = json.loads(response.read())
            print(json.dumps(flows_as_json, indent=4, sort_keys=True))
        else:
            flows_as_json = []

        if len(flows_as_json) > 0:
            flow_list = []
            # Append Flow(s) to flow list
            for k in range(0, len(flows_as_json[DPID]) - 1):
                if not (flows_as_json[DPID][k]["match"].get('nw_src') is None):
                    src_ip = flows_as_json[DPID][k]["match"]["nw_src"]
                    dst_ip = flows_as_json[DPID][k]["match"]["nw_dst"]
                    n_packets = flows_as_json[DPID][k]["packet_count"]
                    n_bytes = flows_as_json[DPID][k]["byte_count"]
                    # Append a new flow
                    flow_list.append(Flow(src_ip, dst_ip, n_packets, n_bytes))

            # If there are flows based on src ip
            if len(flow_list) > 0:

                # Features controller to calculate features from collected flows
                fc = FeaturesControllerTraining(flow_list, "137.204.60.10", PERIOD)

                # Get features
                row = []
                features = fc.get_features().get_features_as_array()
                print(features)
                for (k, v) in features:
                    row.append(v)

                # Append Class
                row.append(1)
                # Write into csv
                writer.writerow(row)

                # First clear all flow entries
                conn = http.client.HTTPConnection("localhost", 8080)
                conn.request("DELETE", "/stats/flowentry/clear/1")
                # Then add Packet-In flow
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

        time.sleep(PERIOD)


if __name__ == "__main__":
    build_dataset()
