import pickle

import pandas as pd
import yaml
from dvclive import Live
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline


def evaluate_model(model: Pipeline, housing_test: pd.DataFrame) -> float:
    X_test = housing_test.drop("price", axis=1)
    y_test = housing_test["price"]

    mse = mean_squared_error(y_test, model.predict(X_test))

    return mse


if __name__ == "__main__":
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    housing_test = pd.read_csv(params["data_test_path"])
    with open(params["model_path"], "rb") as f:
        model = pickle.load(f)

    mse = evaluate_model(model, housing_test)

    with Live("metrics") as live:
        live.log_metric("mse", mse)
