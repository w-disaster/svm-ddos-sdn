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
while True:
    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("GET", "/stats/flow/1")
    response = conn.getresponse()
    #print(response.status, response.reason)
    json_response = json.loads(response.read())
    print(json.dumps(json_response, indent=4, sort_keys=True))
    time.sleep(SLEEP_SEC)
