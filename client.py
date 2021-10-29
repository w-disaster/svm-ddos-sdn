#import pycurl
#from io import BytesIO 

#b_obj = BytesIO() 
#crl = pycurl.Curl() 

# Set URL value
#crl.setopt(crl.URL, 'http://localhost:8080/stats/flow/1')

# Write bytes that are utf-8 encoded
#crl.setopt(crl.WRITEDATA, b_obj)

# Perform a file transfer 
#crl.perform() 

# End curl session
#crl.close()

# Get the content stored in the BytesIO object (in byte characters) 
#get_body = b_obj.getvalue()

# Decode the bytes stored in get_body to HTML and print the result 
#print('Output of GET request:\n%s' % get_body.decode('utf8')) 

import http.client
import time
import json

SLEEP_SEC = 3
i = 0
while True:
    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("GET", "/stats/flow/1")
    response = conn.getresponse()
    #print(response.status, response.reason)
    json_response = json.loads(response.read())
    print("count: " + str(i))
    i = i + 1
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    for k in range(0, len(json_response["1"]) - 1):
        #print(json.dumps(json_response, indent=4, sort_keys=True))
        #print(json.dumps(json_response["1"][k], indent=4, sort_keys=True))

        # Drop all packets that match destination IP == 192.168.1.20
        if json_response["1"][k]["match"]["nw_dst"] == '192.168.1.20':
            filter_flows = json.dumps({
                "dpid": 1,
                "cookie": json_response["1"][k]["cookie"],
                "table_id": json_response["1"][k]["table_id"],
                "idle_timeout": json_response["1"][k]["idle_timeout"],
                "hard_timeout": json_response["1"][k]["hard_timeout"],
                "priority": json_response["1"][k]["priority"],
                "flags": json_response["1"][k]["flags"],
                "match":{
                    "dl_dst": json_response["1"][k]["match"]["dl_dst"],
                    "dl_src": json_response["1"][k]["match"]["dl_src"],
                    #"ipv4__src": json_response["1"][k]["match"]["nw_src"],
                    "ipv4_dst": json_response["1"][k]["match"]["nw_dst"],
                    "in_port": json_response["1"][k]["match"]["in_port"],
                    "nw_proto": json_response["1"][k]["match"]["nw_proto"],
                    "dl_type": json_response["1"][k]["match"]["dl_type"],
                },
                # DROP
                "actions":[]
            })
            print(filter_flows)
            conn = http.client.HTTPConnection("localhost", 8080)
            conn.request("POST", "/stats/flowentry/modify", filter_flows)
            #response = conn.getresponse()
            #print(response.status, response.reason)

    time.sleep(SLEEP_SEC)
