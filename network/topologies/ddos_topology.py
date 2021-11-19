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
    sw1 = net.addSwitch('sw1')
    
    # Adding hosts
    
    for i in range(1, 6):
        h = net.addHost('host' + str(i), custom( CPULimitedHost, cpu=0.1), 
                ip='137.204.0.' + str(i * 10) + '/24')
        #h = net.addHost('host' + str(i), cpu=.2, 
        #        ip='137.204.0.' + str(i * 10) + '/24')
        net.addLink(h, sw1, bw=10)
        h.setMAC("00:00:00:00:00:0" + str(i), h.name + "-eth0")    

    # Connecting switches to external controller
    #net.start()
    #sw1.cmd('ovs-vsctl set-controller ' + sw1.name + ' tcp:192.168.1.17:6653')
    c1 = net.addController("c0", controller=RemoteController, ip="192.168.1.17", port=6653)
    c2 = net.addController("c1", controller=RemoteController, ip="192.168.1.17", port=6633)
    
    c1.start()
    c2.start()

    net.start()

    for h in net.hosts:
        if h.name != "host2":
            h.cmd("bash /home/luca/Desktop/traffic.sh &")

    CLI(net)
    net.stop()


# Main
if __name__ == '__main__':
    setLogLevel('info')
    DDOSNetwork()
