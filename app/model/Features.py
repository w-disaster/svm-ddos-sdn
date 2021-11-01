class Features:
    def __init__(self, ssip, sdfp, sdfb, sfe, rfip):
        self.ssip = ssip
        self.sdfp = sdfp
        self.sdfb = sdfb
        self.sfe = sfe
        self.rfip = rfip

    def get_ssip(self):
        return self.ssip

    def get_sdfp(self):
        return self.sdfp

    def get_sdfb(self):
        return self.sdfb

    def get_sfe(self):
        return self.sfe

    def get_rfip(self):
        return self.rfip
