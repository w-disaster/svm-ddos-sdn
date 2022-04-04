# SVM-DDoS-SDN

## DDoS attacks detection based on SVM and mitigation in a Software-Defined Network.

Starting from the build of the network topology using Mininet, I make use of the the Ryu ofctl rest API (https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html) 
to aggregate flows from Open vSwitch switches, delete them and add new ones.

Link to the thesis: https://amslaurea.unibo.it/24691/

### Training

Support Vector Machines (SVMs) are one of many machine learning methods to detect DDoS attacks in a Software-Defined Network.
The parameters used to train the SVM are:
- Speed of source IPs;
- Standard deviation of the number of packets per flow entry;
- Standard deviation of the number of bytes per flow entry;
- Speed of creation of flow entries;
- Ratio of pair-flow.

To simulate normal traffic the script ```gen_traffic.sh``` sets Mininet hosts network namespace visible and runs a script to each one that makes use of ```hping3``` to send a random number of icmp packets with different bytes.
On the other hand, the attack traffic uses 
```
hping3 --flood --rand-source --icmp h_target
``` 
from a Mininet host.

The dataset is composed of 1500 istances of normal traffic and only 500 of attack because in this case the parameters assume similar values.

In order to calulate features, in the Open vSwitch are installed by C1 flow entries with src IP, dst IP as matching field. Then, from each flow entry it's possible 
to sample the packet count and byte count using the Ryu ofctl API. The python script ```train.py``` samples the switch every 3s through the API and builds the dataset.

### Application

The python-based application uses the MVC pattern to better organize the code and its main class is ```DDoSControllerThread```.
This class at runtime is a unique thread and it's implemented by an Asynchronous Final State Machine.
The states are 3:
- UNCERTAIN;
- NORMAL: in this state the SVM classifier predicted the traffic as normal. The features are real-time plotted in a Tkinter window and legitimate source IPs are stored in an array;
- ANOMAOUS: the SVM classifier predicted the traffic as attack. The features are plotted and mitigation is applied. The mitigation consists of the install of a DROP entry that matches with all packets with dst IP equal to target host IP. Then, the connection for all the legitimate IPs stored in the NORMAL state is maintained to allow them to keep the connection with the server.


### Experimentation topology

![progetto_finale_dettagliato](https://user-images.githubusercontent.com/48534936/144596452-8d7acfbc-2db2-4955-9b4e-16c710f72454.png)

Start the controllers in the host:

C1: 
``` 
ryu-manager --ofp-tcp-listen-port 6653 c1.py
```

C2: 
```
ryu-manager --ofp-tcp-listen-port 6633 c2.py ofctl_rest.py
```

Start the topology in the guest in order to maintain CPU resources when the attack occurs and run normal traffic script:

```
sudo mn --custom mn_ddos_topology.py --switch ovsk \
  --controller=remote,ip=192.168.1.17:6653 \
  --controller=remote,ip=192.168.1.17:6633 --topo ddostopo
```
```
sudo bash gen_traffic.sh 137.204.10.100
```


In conclusion, start the application.
