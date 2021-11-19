#!/usr/bin/python3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn import metrics

# Read csv file
df = pd.read_csv('classifier/dataset.csv')

# Read columns and build matrix
X = np.c_[df["speed_src_ip"], df["std_n_packets"],
          df["std_bytes"], df["bytes_per_flow"], df["n_int_flows"]]
y = df["class"]

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5,
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

anomalous = []
normal = []
for i, row in enumerate(X_test):
    if y_pred[i] == 1:
        anomalous.append((X_test[i, 1], X_test[i, 2]))
    else:
        normal.append((X_test[i, 1], X_test[i, 2]))

plt.plot([x for (x, y) in anomalous], [y for (x, y) in anomalous], "r+", label="anomalous")
plt.plot([x for (x, y) in normal], [y for (x, y) in normal], "g+", label="normal")

plt.xlim(0, 1)
plt.ylim(0, 250)
plt.title("SVM classification on test set")
plt.xlabel('SDFP')
plt.ylabel('SDFB')
plt.legend(loc="upper right")
plt.show()