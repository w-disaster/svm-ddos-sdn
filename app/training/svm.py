import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn import metrics

# Read csv file
df = pd.read_csv('dataset.csv')

# Read columns and build matrix
X = np.c_[df["speed_src_ip"], df["std_n_packets"], df["std_bytes"], 
        df["bytes_per_flow"], df["n_int_flows"]]
y = df["class"]

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, 
        random_state=0)

""" Create classifier with: 
    - linear kernel 
    - C = 1 (default) as the regularization parameter
"""
clf = SVC(kernel='linear', random_state=0)

# Train the model
clf.fit(X_train, y_train)

# Predict test set and calculate accuracy
y_pred = clf.predict(X_test)
print("Accuracy: ", metrics.accuracy_score(y_test, y_pred))

# Save the model into a file
f = 'model.sav'
joblib.dump(clf, f)
