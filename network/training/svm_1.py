import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn import metrics

def plot_svc_decision_function(model, ax=None, plot_support=True):
    """Plot the decision function for a 2D SVC"""
    if ax is None:
        ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # create grid to evaluate model
    x = np.linspace(xlim[0], xlim[1], 30)
    y = np.linspace(ylim[0], ylim[1], 30)
    Y, X = np.meshgrid(y, x)
    xy = np.vstack([X.ravel(), Y.ravel()]).T
    P = model.decision_function(xy).reshape(X.shape)
    
    # plot decision boundary and margins
    ax.contour(X, Y, P, colors='k',
               levels=[-1, 0, 1], alpha=0.5,
               linestyles=['--', '-', '--'])
    
    # plot support vectors
    if plot_support:
        ax.scatter(model.support_vectors_[:, 0],
                   model.support_vectors_[:, 1],
                   s=300, linewidth=1, facecolors='none');
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)


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


plt.scatter(X[:, 3], X[:, 4], c=y, s=4000, cmap='autumn')
plot_svc_decision_function(clf)
