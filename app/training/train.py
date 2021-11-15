#!/usr/bin/python3
import csv
import http
import json
import time

from app.controllers.FeaturesControllerTraining import FeaturesControllerTraining
from app.model.Flow import Flow

# Variables
MAX_SAMPLES = 1000
SAMPLING_PERIOD = 3
DPID = "1"
TARGET_IP = "137.204.10.100"
f = open('normal_dataset_final.csv', 'w')
writer = csv.writer(f)


# Delete all flow entries and add Packet In flow
def del_flows_add_packet_in():
    # Clear all flow entries
    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("DELETE", "/stats/flowentry/clear/1")
   
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


def read_sample(sample_as_json):
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


def build_dataset():
    del_flows_add_packet_in()
    time.sleep(SAMPLING_PERIOD)
    
    # Collect MAX_SAMPLES samples
    for i in range(1, MAX_SAMPLES):
        # Get all flows
        conn = http.client.HTTPConnection("localhost", 8080)
        conn.request("GET", "/stats/flow/1")
        response = conn.getresponse()

        # Read response
        if response.status == 200:
            sample_as_json = json.loads(response.read())
        else:
            sample_as_json = []

        if len(sample_as_json) > 0:
            # Read sample
            sample = read_sample(sample_as_json)
            # If there are flows based on src ip
            if len(sample) > 0:
                # Features controller to calculate features from collected flows
                fc = FeaturesControllerTraining(sample, TARGET_IP, SAMPLING_PERIOD)

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

                # Delete flow entries, add Packet In
                del_flows_add_packet_in()

        time.sleep(SAMPLING_PERIOD)


if __name__ == "__main__":
    build_dataset()
