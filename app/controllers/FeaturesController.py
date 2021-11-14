import time

import numpy as np
from app.model.Features import Features


class FeaturesController:
    def __init__(self, period, target_ip):
        self.period_flows = {}
        self.old_period_flows = {}
        self.period = period
        self.target_ip = target_ip
        self.first_sample_set = False

    def add_sample(self, flows, flag):
        for i, flow in enumerate(flows):
            # If the flow already exists
            if (flow.get_src_ip(), flow.get_dst_ip()) in self.period_flows:
                # Calculate the number of packets passed in the period T
                local_flow_n_packets = flow.get_n_packets() - \
                                       self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["n_packets"]

                # If it's not equal to 0 then set the number of packets and bytes passed in the period T
                if local_flow_n_packets > 0:
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["diff_n_packets"] = local_flow_n_packets
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["diff_n_bytes"] = flow.get_n_bytes() - \
                        self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["n_bytes"]

                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["n_packets"] = flow.get_n_packets()
                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["n_bytes"] = flow.get_n_bytes()

                else:
                    # Else delete the flow == do not consider it for the features computation
                    old_flow = self.period_flows.pop((flow.get_src_ip(), flow.get_dst_ip()))
                    if (flow.get_src_ip(), flow.get_dst_ip()) not in self.old_period_flows:
                        self.old_period_flows[(flow.get_src_ip(), flow.get_dst_ip())] = old_flow

            else:
                # If there isn't add it
                is_in_old = (flow.get_src_ip(), flow.get_dst_ip()) in self.old_period_flows

                if is_in_old:
                    diff_packets = flow.get_n_packets() - \
                           self.old_period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["n_packets"]
                else:
                    diff_packets = 0

                if not is_in_old:
                    if self.is_first_sample_set():
                        self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())] = \
                            {"n_packets": flow.get_n_packets(), "diff_n_packets": flow.get_n_packets(),
                                "n_bytes": flow.get_n_bytes(), "diff_n_bytes": flow.get_n_bytes()}
                    else:
                        self.first_sample_set = True
                        self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())] = \
                            {"n_packets": flow.get_n_packets(), "diff_n_packets": 0,
                                "n_bytes": flow.get_n_bytes(), "diff_n_bytes": 0}

                elif diff_packets > 0:
                    diff_bytes = flow.get_n_bytes() - \
                           self.old_period_flows[(flow.get_src_ip(), flow.get_dst_ip())]["n_bytes"]

                    self.period_flows[(flow.get_src_ip(), flow.get_dst_ip())] =  \
                        {"n_packets": flow.get_n_packets(), "diff_n_packets": diff_packets,
                            "n_bytes": flow.get_n_bytes(), "diff_n_bytes": diff_bytes}

                    self.old_period_flows.pop((flow.get_src_ip(), flow.get_dst_ip()))

        #print(self.period_flows)
        #print(len(self.period_flows))
        # Delete period flow that has expired
        #for pf in self.period_flows:
        #    if pf not in [(flow.src_ip, flow.dst_ip) for flow in flows]:
        #        self.period_flows.pop(pf)
    def clear_fields(self):
        self.period_flows = {}
        self.old_period_flows = {}

    def is_first_sample_set(self):
        return self.first_sample_set

    def get_features(self):
        return Features(self.__ssip(), self.__sdfp(), self.__sdfb(),
                        self.__sfe(), self.__rfip())

    def __ssip(self):
        count_src_ips = 0
        for (src_ip, dst_ip) in self.period_flows:
            if src_ip != self.target_ip:
                count_src_ips += 1
        return count_src_ips / self.period

    def __sdfp(self):
        n_packets = []
        for pf in self.period_flows.values():
            n_packets.append(pf["diff_n_packets"])
        print(n_packets)
        return np.std(n_packets) if len(n_packets) > 0 else 0

    def __sdfb(self):
        n_bytes = []
        for pf in self.period_flows.values():
            n_bytes.append(pf["diff_n_bytes"])
        print(n_bytes)
        return np.std(n_bytes) if len(n_bytes) > 0 else 0

    def __sfe(self):
        return len(self.period_flows) / self.period

    def __rfip(self):
        if len(self.period_flows) == 0:
            return 1
        n_int_flows = 0
        for (src_ip, dst_ip) in self.period_flows:
            if (dst_ip, src_ip) in self.period_flows:
                n_int_flows += 1
        return float(n_int_flows) / len(self.period_flows)

