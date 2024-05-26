import pickle

import pandas as pd
import yaml
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler


def train(housing_train: pd.DataFrame, n_estimators: int) -> None:
    X_train = housing_train.drop("price", axis=1)
    y_train = housing_train["price"]

    model = Pipeline(
        [
            ("scaler", MinMaxScaler()),
            ("predictor", GradientBoostingRegressor(n_estimators=n_estimators)),
        ]
    )
    model.fit(X_train, y_train)

    return model


if __name__ == "__main__":
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)["train"]

    housing_train = pd.read_csv(params["data_train_path"])
    model = train(housing_train, params["n_estimators"])

    with open(params["model_path"], "wb") as f:
        pickle.dump(model, f)
