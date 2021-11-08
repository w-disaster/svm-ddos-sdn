# svm-ddos-sdn

## DDoS attacks detection using SVM and mitigation into a SDN network

In this project I present one of the algorithms used to detect DDoS attacks in a network.

Starting from the build of the network topology using Mininet, I make use of the the Ryu ofctl rest API (https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html) 
to aggregate flows from Open vSwitch switches, delete them and add new ones.
