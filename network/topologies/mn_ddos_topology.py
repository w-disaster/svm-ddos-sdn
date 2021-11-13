from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import RemoteController

class DDOSTopo(Topo):
    "Simple topology example."
    
    def __init__(self, **opts):
        # Initialize topology and default optioe
        Topo.__init__(self, **opts)

        s0 = self.addSwitch("s0", dpid="1")

        for i in range(1, 6):
            s = self.addSwitch("s" + str(i), dpid=str(i + 1))
            for k in range(1, 6):
                h = self.addHost('h' + str(i) + str(k), ip='137.204.' + str(i * 10) + 
                    '.' + str(k * 10) + '/16') 
                self.addLink(h, s, bw=10, delay="10ms")
            self.addLink(s, s0, bw=10, delay="10ms")

        # Add target host
        h_target = self.addHost('h_target', ip='137.204.60.10/16')
        self.addLink(h_target, s0, bw=10, delay="10ms")

 
if __name__ == '__main__':
    ddostopo = DDOSTopo()
    #topos = { 'mytopo': ( lambda: MyTopo() ) }
    net = Mininet(topo=ddostopo,
            controller=None)
    
    net.addController("c0",
                      controller=RemoteController,
                      ip="127.0.0.1",
                      port=6653)

    net.addController("c1",
                      controller=RemoteController,
                      ip="127.0.0.1",
                      port=6633)

    net.start()

    for h in net.hosts:
        if h.name != "h_target":
            h.cmd("bash ./traffic.sh 137.204.60.10  &")
 

    CLI(net)
    net.stop()
