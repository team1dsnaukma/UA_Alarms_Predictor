from sklearn.model_selection import TimeSeriesSplit
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier



def display_metrics(model, X_test, y_test):
    y_pred = model.predict(X_test)
    fpr, tpr, _thersholds = metrics.roc_curve(y_test, y_pred)
    cm_list =  confusion_matrix(y_test, y_pred)
    fig = plt.figure(figsize = (12,7))
    cm_plot = sns.heatmap(cm_list, annot=True, cmap = "Blues_r")
    cm_plot.set_xlabel("Predicted values")
    cm_plot.set_ylabel("Actual values")
    plt.show()

    report = classification_report(y_test, y_pred, target_names=["Actual", "Pred"])
    print(report)

data = pd.read_csv('data_final.csv', index_col=0)
data = data.drop(["date", "region_id", "day_datetime"], axis = 1)
data.fillna(0, inplace = True)

X = data.drop("is_alarm", axis = 1)

y = data["is_alarm"]


tss = TimeSeriesSplit(n_splits=5)

for train_index, test_index in tss.split(data):

    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]


# LogisticRegresion
LR = LogisticRegression(max_iter=100, penalty='l2')
LR.fit(X_train, y_train)
predicted_labels = LR.predict(X_test)
accuracy = (predicted_labels == y_test).mean()
print(accuracy)
print("Accuracy:", accuracy)
with open("../models/LR.pkl", "wb") as lr:
    pickle.dump(LR, lr)


# LinearRegresion
LinR = LinearRegression()
LinR.fit(X_train, y_train)
predicted_labels = LinR.predict(X_test)
accuracy = (predicted_labels == y_test).mean()
with open("../models/LinR.pkl", "wb") as linr:
    pickle.dump(LinR, linr)