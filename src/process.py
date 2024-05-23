import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

BINARY_COLUMNS = [
    "mainroad",
    "guestroom",
    "basement",
    "hotwaterheating",
    "airconditioning",
    "prefarea",
]

CATEGORY_COLUMNS = [
    "furnishingstatus",
]


def process_housing(housing: pd.DataFrame) -> pd.DataFrame:
    housing = housing.copy()

    # Binary encoding
    for col in BINARY_COLUMNS:
        housing[col] = housing[col].apply(lambda x: 1 if x == "yes" else 0)

    # One-hot encoding
    housing = pd.get_dummies(housing, columns=CATEGORY_COLUMNS)

    # Logarize price
    housing["price"] = housing["price"].apply(lambda x: np.log(x) + 1)

    return housing


def split_data(housing: pd.DataFrame, test_size: float, seed: int) -> pd.DataFrame:
    train, test = train_test_split(housing, test_size=test_size, random_state=seed)

    return train, test


if __name__ == "__main__":
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)

    housing = pd.read_csv(params["data_source_path"])

    housing_processed = process_housing(housing)
    housing_train, housing_test = split_data(
        housing_processed, params["test_size"], params["seed"]
    )

    housing_train.to_csv(params["data_train_path"], index=False)
    housing_test.to_csv(params["data_test_path"], index=False)
