import numpy as np

from app.model.Features import Features


class FeaturesController:
    def __init__(self, src_ips, dst_ips, n_packets_per_flow, bytes_per_flow, n_ip_flows, period):
        self.src_ips = src_ips
        self.dst_ips = dst_ips
        self.n_packets_per_flow = n_packets_per_flow
        self.bytes_per_flow = bytes_per_flow
        self.n_ip_flows = n_ip_flows
        self.period = period

    def get_features(self):
        return Features(self.__get_ssip(), self.__get_sdfp(), self.__get_sdfb(),
                        self.__get_sfe(), self.__get_rfip())

    def __get_ssip(self):
        return len(self.src_ips) / self.period

    def __get_sdfp(self):
        return np.std(self.n_packets_per_flow)

    def __get_sdfb(self):
        return np.std(self.bytes_per_flow)

    def __get_sfe(self):
        return self.n_flows / self.period

    def __get_rfip(self):
        n_int_flows = 0
        for ip in self.src_ips:
            if ip not in self.dst_ips:
                n_int_flows += 1
        return float(n_int_flows) / self.n_flows

