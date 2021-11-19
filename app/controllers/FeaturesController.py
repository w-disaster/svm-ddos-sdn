import time

import numpy as np
from app.model.Features import Features


class FeaturesController:
    def __init__(self, period):
        self.period = period
        self.period_flows = {}
        self.old_period_flows = {}
        self.dst_ip_count = {}
        self.most_targeted_ip = None

    def add_sample(self, flows):
        for i, flow in enumerate(flows):
            # If the flow already exists
            if (flow.get_src_ip(), flow.get_dst_ip()) in self.period_flows:
                # Calculate the number of packets passed in the period T
                local_flow_packet_count = flow.get_packet_count() - \
                                       self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["packet_count"]

                # If it's not equal to 0 then set the number of packets and bytes passed in the period T
                if local_flow_packet_count > 0:
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["diff_packet_count"] = local_flow_packet_count
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["diff_byte_count"] = flow.get_byte_count() - \
                        self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["byte_count"]

                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["packet_count"] = flow.get_packet_count()
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["byte_count"] = flow.get_byte_count()

                else:
                    # Else delete the flow == do not consider it for the features computation
                    old_flow = self.period_flows.pop((flow.get_src_ip(), flow.get_dst_ip()))
                    if (flow.get_src_ip(), flow.get_dst_ip()) not in self.old_period_flows:
                        self.old_period_flows[(flow.get_src_ip(), flow.get_dst_ip())] = old_flow

            else:
                # If there isn't add it
                is_in_old = (flow.get_src_ip(), flow.get_dst_ip()) in self.old_period_flows

                if is_in_old:
                    diff_packets = flow.get_packet_count() - \
                           self.old_period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["packet_count"]
                else:
                    diff_packets = 0

                if not is_in_old:
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())] = \
                        {"packet_count": flow.get_packet_count(), "diff_packet_count": flow.get_packet_count(),
                            "byte_count": flow.get_byte_count(), "diff_byte_count": flow.get_byte_count()}

                elif diff_packets > 0:
                    diff_bytes = flow.get_byte_count() - \
                           self.old_period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["byte_count"]

                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())] =  \
                        {"packet_count": flow.get_packet_count(), "diff_packet_count": diff_packets,
                            "byte_count": flow.get_byte_count(), "diff_byte_count": diff_bytes}

                    self.old_period_flows.pop((flow.get_src_ip(), flow.get_dst_ip()))

    def get_features(self):
        return Features(self.__ssip(), self.__sdfp(), self.__sdfb(),
                        self.__sfe(), self.__rfp())

    def get_most_targeted_ip(self):
        self.__compute_most_targeted_ip()
        return self.most_targeted_ip

    def __compute_most_targeted_ip(self):
        self.dst_ip_count = {}
        for (src_ip, dst_ip) in self.period_flows:
            if dst_ip in self.dst_ip_count:
                self.dst_ip_count[dst_ip] += 1
            else:
                self.dst_ip_count[dst_ip] = 1

        v = list(self.dst_ip_count.values())
        k = list(self.dst_ip_count.keys())
        self.most_targeted_ip = k[v.index(max(v))]

    def __ssip(self):
        return self.dst_ip_count[self.most_targeted_ip] / self.period

    def __sdfp(self):
        packet_count = []
        for pf in self.period_flows.values():
            packet_count.append(pf["diff_packet_count"])
        return np.std(packet_count) if len(packet_count) > 0 else 0

    def __sdfb(self):
        byte_count = []
        for pf in self.period_flows.values():
            byte_count.append(pf["diff_byte_count"])
        return np.std(byte_count) if len(byte_count) > 0 else 0

    def __sfe(self):
        return len(self.period_flows) / self.period

    def __rfp(self):
        if len(self.period_flows) == 0:
            return 1
        n_int_flows = 0
        for (src_ip, dst_ip) in self.period_flows:
            if (dst_ip, src_ip) in self.period_flows:
                n_int_flows += 1
        return float(n_int_flows) / len(self.period_flows)

