import joblib
from app.model.TrafficState import TrafficState


class SVMController:
    def __init__(self):
        self.filename = '../training/classifier/model.sav'
        self.clf = joblib.load(self.filename)
        
    def predict(self, features):
        return TrafficState(self.clf.predict(features))
