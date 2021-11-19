
class Flow:
    def __init__(self, src_ip, dst_ip, packet_count, byte_count):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.packet_count = packet_count
        self.byte_count = byte_count

    def get_src_ip(self):
        return self.src_ip

    def get_dst_ip(self):
        return self.dst_ip

    def get_packet_count(self):
        return self.packet_count

    def get_byte_count(self):
        return self.byte_count
