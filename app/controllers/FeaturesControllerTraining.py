import numpy as np

from app.model.Features import Features


class FeaturesControllerTraining:
    def __init__(self, flow_list, target_ip, period):
        self.flow_list = flow_list
        self.target_ip = target_ip
        self.period = period

    def get_features(self):
        return Features(self.__get_ssip(), self.__get_sdfp(), self.__get_sdfb(),
                        self.__get_sfe(), self.__get_rfip())

    def __get_ssip(self):
        count_src_ips = 0
        for flow in self.flow_list:
            if flow.get_src_ip() != self.target_ip:
                count_src_ips += 1
        return count_src_ips / self.period

    def __get_sdfp(self):
        n_packets = []
        for flow in self.flow_list:
            n_packets.append(flow.get_n_packets())
        return np.std(n_packets)

    def __get_sdfb(self):
        n_bytes = []
        for flow in self.flow_list:
            n_bytes.append(flow.get_n_bytes())
        return np.std(n_bytes)

    def __get_sfe(self):
        return len(self.flow_list) / self.period

    def __get_rfip(self):
        n_int_flows = 0
        for uni_flow in self.flow_list:
            for bi_flow in self.flow_list:
                if uni_flow.get_src_ip() == bi_flow.get_dst_ip() and uni_flow.get_dst_ip() == bi_flow.get_src_ip():
                    n_int_flows += 1
        return float(n_int_flows) / len(self.flow_list)
