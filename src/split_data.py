import pandas as pd
import yaml
from sklearn.model_selection import train_test_split


def split_data(housing: pd.DataFrame, test_size: float, seed: int) -> pd.DataFrame:
    train, test = train_test_split(housing, test_size=test_size, random_state=seed)

    return train, test


if __name__ == "__main__":
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)["split_data"]
    housing_processed = pd.read_csv(params["data_processed_path"])

    housing_train, housing_test = split_data(
        housing_processed, params["test_size"], params["seed"]
    )

    housing_train.to_csv(params["data_train_path"], index=False)
    housing_test.to_csv(params["data_test_path"], index=False)
