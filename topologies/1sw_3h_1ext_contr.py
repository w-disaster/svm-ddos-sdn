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

def myNetwork():
    info( 'Creating empty network..\n' )
    net = Mininet(topo=None, build=False, link=TCLink)
    sw1 = net.addSwitch('sw1')
    # Adding hosts
    h1 = net.addHost('host1', ip='192.168.1.10/24')
    h2 = net.addHost('host2', ip='192.168.1.20/24')
    h3 = net.addHost('host3', ip='192.168.1.30/24')
    # Connecting hosts to switches and switch to switch
    net.addLink(h1, sw1)
    net.addLink(h2, sw1)
    net.addLink(h3, sw1)

    h1.setMAC("00:00:00:00:00:01", h1.name + "-eth0")
    h2.setMAC("00:00:00:00:00:02", h2.name + "-eth0")
    h3.setMAC("00:00:00:00:00:03", h3.name + "-eth0")

    for h in net.hosts:
        print("disable ipv6")
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    for sw in net.switches:
        print("disable ipv6")
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    # Connecting switches to external controller
    net.start()
    sw1.cmd('ovs-vsctl set-controller ' +  sw1.name + ' tcp:127.0.0.1:6653')
    CLI(net)
    net.stop()

#Main
if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
