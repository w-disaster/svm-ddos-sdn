
class Flow:
    def __init__(self, src_ip, dst_ip, n_packets, n_bytes):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.n_packets = n_packets
        self.n_bytes = n_bytes

    def get_src_ip(self):
        return self.src_ip

    def get_dst_ip(self):
        return self.dst_ip

    def get_n_packets(self):
        return self.n_packets

    def get_n_bytes(self):
        return self.n_bytes
