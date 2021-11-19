from enum import Enum


class Feature(Enum):
    SSIP = "Speed of source IP"
    SDFP = "Standard deviation of flow packets"
    SDFB = "Standard deviation of flow bytes"
    SFE = "Speed of flow entries"
    RFIP = "Ratio of pair-flow"


class Features:
    def __init__(self, ssip, sdfp, sdfb, sfe, rfp):
        self.ssip = ssip
        self.sdfp = sdfp
        self.sdfb = sdfb
        self.sfe = sfe
        self.rfp = rfp

    def get_features_as_array(self):
        return [(Feature.SSIP, self.ssip), (Feature.SDFP, self.sdfp),
                (Feature.SDFB, self.sdfb), (Feature.SFE, self.sfe), (Feature.RFIP, self.rfp)]

    def get_ssip(self):
        return self.ssip

    def get_sdfp(self):
        return self.sdfp

    def get_sdfb(self):
        return self.sdfb

    def get_sfe(self):
        return self.sfe

    def get_rfp(self):
        return self.rfp
