import http.client
import time
import json
from app.model.Features import Features
from queue import Queue
import pandas as pd
import csv
import joblib
import threading


class MainController:
    def __init__(self, queue, period):
        self.queue = queue
        self.period = period
        
    def run(self):
        dpid = "1"
        n_flows = 0
        filename = '../controllers/model.sav'
        loaded_model = joblib.load(filename)

        header = ["SSIP", "Stdevpack", "Stdevbyte", "NbFlow", "NbIntFlow"]

        while True:
            conn = http.client.HTTPConnection("localhost", 8080)
            conn.request("GET", "/stats/flow/1")
            response = conn.getresponse()
            print(response.status, response.reason)

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
                    if json_response[dpid][k]["match"] != "":
                        #print(json.dumps(json_response[dpid][k], indent=4, sort_keys=True))
                        src_ips.append(json_response[dpid][k]["match"]["nw_src"])
                        dst_ips.append(json_response[dpid][k]["match"]["nw_dst"])
                        n_packets_per_flow.append(json_response[dpid][k]["packet_count"])
                        bytes_per_flow.append(json_response[dpid][k]["byte_count"])
                        n_ip_flows = n_ip_flows + 1

                # Features
                features = Features(src_ips=src_ips, dst_ips=dst_ips, n_packets_per_flow=n_packets_per_flow,
                                    bytes_per_flow=bytes_per_flow, n_flows=n_ip_flows, period=self.period)

                # Write row into csv
                row = [features.get_ssip(), features.get_sdfp(), features.get_sdfb(), features.get_sfe(),
                       features.get_rfip()]

                # Update View
                self.queue.put([("timestamp", time.time()), ("ssip", row[0]), ("sdfp", row[1]), ("sdfb", row[2]),
                                ("sfe", row[3]), ("rfip", row[4])])

                with open('live.csv', 'w') as datafile:
                    writer = csv.writer(datafile, delimiter=",")
                    writer.writerow(header)
                    writer.writerow(row)

                dataset = pd.read_csv('live.csv')
                result = loaded_model.predict(dataset)
                if result[0] == 1:
                    print("anomalous")

                    # print(json.dumps(json_response, indent=4, sort_keys=True))
                    for k in range(0, len(json_response[dpid]) - 1):
                        # print(json.dumps(json_response, indent=4, sort_keys=True))
                        # print(json.dumps(json_response[dpid][k], indent=4, sort_keys=True))

                        # Drop all packets that match destination IP == 192.168.1.20
                        if json_response[dpid][k]["match"]["nw_dst"] == '192.168.1.20':
                            filter_flows = json.dumps({
                                "dpid": 1,
                                "cookie": json_response[dpid][k]["cookie"],
                                "table_id": json_response[dpid][k]["table_id"],
                                "idle_timeout": json_response[dpid][k]["idle_timeout"],
                                "hard_timeout": json_response[dpid][k]["hard_timeout"],
                                "priority": json_response[dpid][k]["priority"],
                                "flags": json_response[dpid][k]["flags"],
                                "match": {
                                    "dl_dst": json_response[dpid][k]["match"]["dl_dst"],
                                    "dl_src": json_response[dpid][k]["match"]["dl_src"],
                                    # "ipv4__src": json_response[dpid][k]["match"]["nw_src"],
                                    "ipv4_dst": json_response[dpid][k]["match"]["nw_dst"],
                                    "in_port": json_response[dpid][k]["match"]["in_port"],
                                    "nw_proto": json_response[dpid][k]["match"]["nw_proto"],
                                    "dl_type": json_response[dpid][k]["match"]["dl_type"],
                                },
                                # DROP
                                "actions": []
                            })
                            # print(filter_flows)
                            conn = http.client.HTTPConnection("localhost", 8080)
                            conn.request("POST", "/stats/flowentry/modify", filter_flows)
                            # response = conn.getresponse()
                            # print(response.status, response.reason)
                else:
                    print("normal")

            time.sleep(self.period)


#if __name__ == "__main__":
#    c = MainController()