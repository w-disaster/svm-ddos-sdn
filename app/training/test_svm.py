from sklearn import datasets
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn import metrics

# Load cancer dataset
cancer = datasets.load_breast_cancer()

# Print the features and target names
print("Features: ", cancer.feature_names, "\nLabels: ", cancer.target_names)

# Get values
X = cancer.data
y = cancer.target

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

""" Create classifier with:
    - linear kernel
    - C = 1 (default) as regularization parameter
"""
clf = SVC(kernel='linear', random_state=0)

# Train the model
clf.fit(X_train, y_train)

# Predict test set and calculate accuracy 
y_pred = clf.predict(X_test)
print("Accuracy: ", metrics.accuracy_score(y_test, y_pred))
