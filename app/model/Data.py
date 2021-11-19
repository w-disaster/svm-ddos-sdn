class Data:
    def __init__(self, timestamp, features, traffic_state):
        self.timestamp = timestamp
        self.features = features
        self.traffic_state = traffic_state

    def get_timestamp(self):
        return self.timestamp

    def get_features(self):
        return self.features

    def get_traffic_state(self):
        return self.traffic_state
