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


def predict(model, input_data):
    return model.predict(input_data)


# train model
model = train_model('yourfile.csv')


def my_handler(keys: list[str], datum: Datum) -> Messages:
    val = datum.value
    _ = datum.event_time
    _ = datum.watermark
    messages = Messages()
    messages.append(Message(value=val, keys=keys))
    return messages


if __name__ == "__main__":
    grpc_server = Mapper(handler=my_handler)
    grpc_server.start()
