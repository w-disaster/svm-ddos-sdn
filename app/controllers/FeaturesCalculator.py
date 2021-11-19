import numpy as np

from app.model.Features import Features


class FeaturesControllerTraining:
    def __init__(self, sample, target_ip, sampling_period):
        self.sample = sample
        self.target_ip = target_ip
        self.sampling_period = sampling_period

    def get_features(self):
        return Features(self.__get_ssip(), self.__get_sdfp(), self.__get_sdfb(),
                        self.__get_sfe(), self.__get_rfp())

    def __get_ssip(self):
        count_src_ips = 0
        for flow in self.sample:
            if flow.get_dst_ip() == self.target_ip:
                count_src_ips += 1
        return count_src_ips / self.sampling_period

    def __get_sdfp(self):
        packet_count = []
        for flow in self.sample:
            packet_count.append(flow.get_packet_count())
        return np.std(packet_count)

    def __get_sdfb(self):
        byte_count = []
        for flow in self.sample:
            byte_count.append(flow.get_byte_count())
        return np.std(byte_count)

    def __get_sfe(self):
        return len(self.sample) / self.sampling_period

    def __get_rfp(self):
        n_int_flows = 0
        for uni_flow in self.sample:
            for bi_flow in self.sample:
                if uni_flow.get_src_ip() == bi_flow.get_dst_ip() and uni_flow.get_dst_ip() == bi_flow.get_src_ip():
                    n_int_flows += 1
        return float(n_int_flows) / len(self.sample)
