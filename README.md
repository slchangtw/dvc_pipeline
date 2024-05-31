# DVC Pipeline using House Prices dataset from Kaggle

This project demonstrates how to use DVC to create a pipeline for a machine learning project. The dataset used is the House Prices dataset from Kaggle. The pipeline consists of the following steps:
1. Processing data
2. Splitting the data into training and testing sets
3. Training a model
4. Evaluating the model

## Downloading the dataset

1. The dataset can be downloaded from [Kaggle](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset).
2. Unzip the dataset and place it in the `data/source` directory.

## Setting up the environment

1. Create a virtual environment with Python 3.11 and activate it.

```bash
python -m venv .venv
. .venv/bin/activate
```

2. Install package manager `poetry` and install the dependencies. You can check the dependencies in the `pyproject.toml` file.

```bash
pip install poetry
poetry install
```

## Add remote storage

You can use remote storage to manage your data. In this project, we use AWS S3 as an example. The following command adds this remote storage to the project. `s3://dvc-pipline` is a bucket already created in AWS S3.
```bash
dvc remote add remote_storage s3://dvc-pipline
```

In `.dvc/config` file, you can see the remote storage configuration.

```yaml
[core]
    remote = remote_storage
['remote "remote_storage"']
    url = s3://dvc-pipline
```

## Taking a look at the pipeline

The `dvc.yaml` file defines the pipeline that consists of multiple stages. Each stage in our workflow consists of a command to be executed, along with its dependencies, parameters, and outputs. Let's take the `process` stage as an example.

```yaml
process:
    cmd: python src/process.py # The command to be executed
    deps: # Required files
    - data/source/Housing.csv
    params: # Used parameters defined in param.yaml
    - process.data_source_path
    - process.data_processed_path
    outs: # Output files
    - data/processed/processed.csv
```

> The data and produced files in any states are automatically tracked by DVC, so that you don't have to manually track them.

You can visualize the pipeline by running the following command:

```bash
dvc dag
```
```
+-----------------------------+  
| data/source/Housing.csv.dvc |  
+-----------------------------+  
                *                
                *                
                *                
          +---------+            
          | process |            
          +---------+            
                *                
                *                
                *                
        +------------+           
        | split_data |           
        +------------+           
          **        **           
        **            *          
       *               **        
 +-------+               *       
 | train |             **        
 +-------+            *          
          **        **           
            **    **             
              *  *               
          +----------+           
          | evaluate |           
          +----------+          
```

## Running the pipeline

The pipeline can be run by the command `dvc repro`. After the pipeline is run, a state file `dvc.lock` is created as a snapshot of the results. You can check the metrics of the pipeline by running the command `dvc metrics show`. Also, this pipeline generates a feature importance plot in the `metrics/plots` directory.

```
Path                  mse.test    mse.train
metrics/metrics.json  0.06426     0.01621
```
![Imgur Image](https://imgur.com/BNHFxyg.jpg)

## Run experiments with different parameters

1. To run experiments with different numbers of estimators, you can create a queue of experiments by the command below. The `--name` flag helps you to identify the experiment, and the `-S` flag sets the parameters. If you need to set multiple parameters, you can append `-S parameter=value1,value2` to the command.

```bash
dvc exp run \
--name "n-estimator-size-second" \
--queue  \
-S "train.n_estimators=100,150,200"
```

2. Execute the experiments.
```bash
dvc exp run --run-all
```

3. Check the results of the experiments.
```bash
dvc exp show
```
![Imgur Image](https://imgur.com/KuxZjKT.jpg)

## Use DVC Studio to share your experiments

DVC Studio is a web-based interface that helps you to share your machine learning projects with your team. You can follow the steps in this [link](https://dvc.org/doc/studio/user-guide/experiments/create-a-project) to set up DVC Studio.

You can login in DVC Studio in your console by running the command below. And if you run the experiments again, you can see the results being automatically pushed in DVC Studio.

```bash
dvc studio login
```