#!/user/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Node
from mininet.node import Host
from mininet.link import TCLink
from mininet.link import Intf
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.util import quietRun
from mininet.node import CPULimitedHost
from mininet.util import custom

def DDOSNetwork():
    info('Creating network..\n')
    net = Mininet(controller=RemoteController, topo=None, build=False, link=TCLink)
   
    c0 = net.addController("c0", controller=RemoteController, 
            ip="127.0.0.1", port=6653)
    c1 = net.addController("c1", controller=RemoteController, 
            ip="127.0.0.1", port=6633)

    # Adding hosts
    s0 = net.addSwitch("s0")
    s0.start([c0, c1])

    for i in range(1, 6):
        s = net.addSwitch("s" + str(i))
        for k in range(1, 6):
            h = net.addHost('h' + str(k), ip='137.204.' + str(i * 10) + 
                '.' + str(k * 10) + '/16') 
            net.addLink(h, s, bw=10)
            #h.setMAC("00:00:00:00:00:0" + str(k), h.name + "-eth0")    
        net.addLink(s, s0, bw=10)
        s.start([c0])

    # Start controllers
    c0.start()
    c1.start()
    # Start network
    net.start()

    # Start to ping
    for h in net.hosts:
        if h.name != "host2":
            h.cmd("ping 137.204.0.20 &")

    CLI(net)
    net.stop()


# Main
if __name__ == '__main__':
    setLogLevel('info')
    DDOSNetwork()
