import numpy as np
import pandas as pd
import yaml

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


if __name__ == "__main__":
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)["process"]

    housing = pd.read_csv(params["data_source_path"])

    housing_processed = process_housing(housing)
    housing_processed.to_csv(params["data_processed_path"], index=False)
