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

def myNetwork():
    info('Creating empty network..\n')
    net = Mininet(topo=None, build=False, link=TCLink)
    sw1 = net.addSwitch('sw1')
    
    # Adding hosts
    
    for i in range(1, 6):
        #h = net.addHost('host' + str(i), custom( CPULimitedHost, cpu=0.1), 
        #        ip='137.204.0.' + str(i * 10) + '/24')
        h = net.addHost('host' + str(i), 
                ip='137.204.0.' + str(i * 10) + '/24')
        net.addLink(h, sw1, bw=1, delay='50ms')
        h.setMAC("00:00:00:00:00:0" + str(i), h.name + "-eth0")    

    # Connecting switches to external controller
    net.start()
    sw1.cmd('ovs-vsctl set-controller ' + sw1.name + ' tcp:127.0.0.1:6653')
    
    for h in net.hosts:
        if h.name != "host2":
            h.cmd("ping 137.204.0.20 &")

    CLI(net)
    net.stop()


# Main
if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
