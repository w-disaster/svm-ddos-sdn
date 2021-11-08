from enum import Enum


class FeatureLabel(Enum):
    SSIP = "Speed of source IPs"
    SDFP = "Standard deviation of flow packets"
    SDFB = "Standard deviation of flow bytes"
    SFE = "Speed of flow entries"
    RFIP = "Ratio of interactive IPs"


class Features:
    def __init__(self, ssip, sdfp, sdfb, sfe, rfip):
        self.ssip = ssip
        self.sdfp = sdfp
        self.sdfb = sdfb
        self.sfe = sfe
        self.rfip = rfip

    def get_features_as_array(self):
        return [(FeatureLabel.SSIP, self.ssip), (FeatureLabel.SDFP, self.sdfp),
                (FeatureLabel.SDFB, self.sdfb), (FeatureLabel.SFE, self.sfe), (FeatureLabel.RFIP, self.rfip)]

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
