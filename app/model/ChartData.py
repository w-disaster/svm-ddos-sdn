class PlotData:
    def __init__(self, timestamp, features, traffic):
        self.timestamp = timestamp
        self.features = features
        self.traffic = traffic

    def get_timestamp(self):
        return self.timestamp

    def get_features(self):
        return self.features

    def get_traffic(self):
        return self.traffic
