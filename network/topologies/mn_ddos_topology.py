from mininet.topo import Topo

N_HOSTS = 25
DPID = "1"
TARGET_IP = "137.204.10.100"

class DDoSTopo(Topo):
    "DDoS experimentation topology"
    
    def build(self):
        # Add one switch
        s0 = self.addSwitch("s0", dpid=DPID)

        # Add hosts and connect them to the switch
        for i in range(1, N_HOSTS + 1):
            h = self.addHost("h" + str(i), ip="137.204.10." + str(i + 1) + "/24") 
            self.addLink(h, s0, bw=10, delay="10ms")
           
        # Add target host
        h_target = self.addHost("h_target", ip=TARGET_IP + "/24")
        self.addLink(h_target, s0, bw=10, delay="10ms")

topos = { 'ddostopo': ( lambda: DDoSTopo() ) }
