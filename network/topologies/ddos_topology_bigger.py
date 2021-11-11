#!/user/bin/python3
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
import sys

def DDOSNetwork(c0_ip, c0_port, c1_ip, c1_port, traffic_filename):
    info('Creating network..\n')
    net = Mininet(controller=RemoteController, topo=None, build=False, link=TCLink)
   
    c0 = net.addController("c0", controller=RemoteController, 
            ip=c0_ip, port=c0_port)
    c1 = net.addController("c1", controller=RemoteController, 
            ip=c1_ip, port=c1_port)

    # Adding hosts
    s0 = net.addSwitch("s0")
    s0.start([c0, c1])

    for i in range(1, 6):
        s = net.addSwitch("s" + str(i))
        for k in range(1, 6):
            h = net.addHost('h' + str(i) + str(k), ip='137.204.' + str(i * 10) + 
                '.' + str(k * 10) + '/16') 
            net.addLink(h, s, bw=10)
            #h.setMAC("00:00:00:00:00:0" + str(k), h.name + "-eth0")    
        net.addLink(s, s0, bw=10)
        s.start([c0])

    # Add target host
    h_target = net.addHost('h_target', ip='137.204.60.10/16')
    net.addLink(h_target, s0, bw=10)

    # Start controllers
    c0.start()
    c1.start()
    # Start network
    net.start()

    # Start to ping
    #for h in net.hosts:
        #if h.name != "h_target":
            #h.cmd("bash " + traffic_filename + " " + h_target.IP() + " &")
            #CLI.do_xterm(h.name)

    CLI(net)
    net.stop()


# Main
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("usage: sudo python3 ddos_topology.py <C0_ip:C0_port> <C1_ip:C1_port> <path/traffic_file.sh>") 
    else:
        # Get C0 and C1 Ip and port
        c0_argv = sys.argv[1].split(":")
        c1_argv = sys.argv[2].split(":")
        print(c0_argv[0], c0_argv[1], c1_argv[0], c1_argv[1])
        if len(c0_argv) > 1 and len(c1_argv) > 1:
            setLogLevel('info')
            DDOSNetwork(c0_argv[0], int(c0_argv[1]), c1_argv[0], int(c1_argv[1]), sys.argv[3])
        else:
            print("usage: sudo python3 ddos_topology.py <C0_ip:C0_port> <C1_ip:C1_port> <path/traffic_file.sh>")

