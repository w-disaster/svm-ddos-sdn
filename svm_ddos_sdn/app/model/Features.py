import numpy as np
import json


class Features:
    def __init__(self, src_ips=None, dst_ips=None, n_packets_per_flow=None, bytes_per_flow=None, n_flows=None,
                 period=None):
        self.src_ips = src_ips
        self.dst_ips = dst_ips
        self.n_packets_per_flow = n_packets_per_flow
        self.bytes_per_flow = bytes_per_flow
        self.n_flows = n_flows
        self.period = period

    def get_ssip(self):
        return len(self.src_ips) / self.period

    def get_sdfp(self):
        return np.std(self.n_packets_per_flow)

    def get_sdfb(self):
        return np.std(self.bytes_per_flow)

    def get_sfe(self):
        return self.n_flows / self.period

    def get_rfip(self):
        n_int_flows = 0
        for ip in self.src_ips:
            if ip not in self.dst_ips:
                n_int_flows += 1
        return float(n_int_flows) / self.n_flows
