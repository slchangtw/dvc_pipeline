# DVC Pipeline using House Prices dataset from Kaggle

This project demonstrates how to use DVC to create a pipeline for a machine learning project. The dataset used is the House Prices dataset from Kaggle. The pipeline consists of the following steps:
1. Processing data and splitting it into training and testing sets
2. Training a model
3. Evaluating the model

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

## Taking a look at the pipeline

The `dvc.yaml` file defines the pipeline that consists of multiple stages. In general, each stage has a command that is executed and the dependencies and outputs of the stage. Taking `process` stage as an example, the command is to run the `process.py` script, the dependencies are the `Housing.csv` file and the `params.yaml` file, and the outputs are the `train.csv` and `test.csv` files. 

> The data and produced files in any states are automatically tracked by DVC, so that you don't have to manually track them.

```yaml
process:
    cmd: python src/process.py
    deps:
    - data/source/Housing.csv
    - params.yaml
    outs:
    - data/train/train.csv
    - data/test/test.csv
```

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

1. The pipeline can be run by the command `dvc repro`. After the pipeline is run, a state file `dvc.lock` is created as a snapshot of the results. You can check the metrics of the pipeline by running the command `dvc metrics show`.

2. If you modify parameters in `params.yaml`, such as n_estimators in the `train` stage, and then run `dvc repro`, the pipeline will execute again with the updated parameter. 
