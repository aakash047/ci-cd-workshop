import json

from pynumaflow.mapper import Messages, Message, Datum, Mapper

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


def train_model(data_path):
    # Load the dataset
    dataset = pd.read_csv(data_path)

    # Assume we want to use the first column as feature (X) and second column as target (y)
    X = dataset.iloc[:, 0:1].values
    y = dataset.iloc[:, 1].values

    # Split the dataset into the training set and test set
    # We're splitting the data in 1/3, so out of 30 rows, 20 rows will go into the training set,
    # and 10 rows will go into the testing set.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1 / 3, random_state=0)

    # Creating the Linear Regression model and fitting it to our training data
    linear_regressor = LinearRegression()
    linear_regressor.fit(X_train, y_train)

    return linear_regressor


# train model
model = train_model('https://raw.githubusercontent.com/veds-g/ci-cd-workshop/master/anomaly-pl/output.csv')


def my_handler(keys: list[str], datum: Datum) -> Messages:
    val = datum.value
    _ = datum.event_time
    _ = datum.watermark
    messages = Messages()
    # value will be in json string convert to dict and extract "le" field which is inside "labels" map
    d = json.loads(val)
    print(d['value'], "\n")
    le = d['value']

    print(int(le), "\n")
    predicted_val = model.predict([[int(le)]])
    print("predicted - ", predicted_val, "\n")
    # create a json like {"anomaly_score": predicted_val}
    output = json.dumps({"anomaly_score": predicted_val[0]}).encode("utf-8")
    messages.append(Message(value=output, keys=keys))
    return messages


if __name__ == "__main__":
    temp = model.predict([[1.5]])
    print(temp)
    grpc_server = Mapper(handler=my_handler)
    grpc_server.start()
