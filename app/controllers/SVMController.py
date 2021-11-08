import joblib


class SVMController:
    def __init__(self):
        self.filename = '../controllers/model.sav'
        self.clf = joblib.load(self.filename)
        
    def predict(self, features):
        return self.clf.predict(features)
