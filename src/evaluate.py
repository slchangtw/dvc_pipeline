import pickle

import pandas as pd
import yaml
from dvclive import Live
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline


def evaluate_model(model: Pipeline, housing: pd.DataFrame) -> float:
    X = housing.drop("price", axis=1)
    y = housing["price"]

    mse = mean_squared_error(y, model.predict(X))

    return mse


def get_feature_importance_plot(model: Pipeline, columns: list[str]):
    fig, axes = plt.subplots(1, 1, figsize=(12, 8))

    importances = model["predictor"].feature_importances_
    forest_importances = pd.Series(importances, index=columns).nlargest(n=7)
    forest_importances.plot.bar(ax=axes)
    axes.set_title("Feature importances")
    fig.tight_layout()

    return fig


if __name__ == "__main__":
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)["evaluate"]

    housing_train = pd.read_csv(params["data_train_path"])
    housing_test = pd.read_csv(params["data_test_path"])
    with open(params["model_path"], "rb") as f:
        model = pickle.load(f)

    with Live("metrics") as live:
        live.summary = {"mse": {}}
        live.summary["mse"]["train"] = evaluate_model(model, housing_train)
        live.summary["mse"]["test"] = evaluate_model(model, housing_test)

        feature_importance = get_feature_importance_plot(
            model, housing_test.drop(["price"], axis=1).columns.to_list()
        )
        live.log_image("importance.png", feature_importance)
