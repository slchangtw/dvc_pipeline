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

You can use remote storage to manage your data. In this project, we use AWS S3 as an example. The following command adds this remote storage to the project. `s3://<bucket name>` is a bucket already created in AWS S3. In this turorial, we use `dvc-pipeline-2024` as the bucket name.
```bash
dvc remote add remote_storage s3://dvc-pipeline-2024
```

In `.dvc/config` file, you can see the remote storage configuration.

```yaml
[core]
    remote = remote_storage
['remote "remote_storage"']
    url = s3://dvc-pipeline-2024
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

## Use DVC Studio to track your experiments

### Setting up DVC Studio and adding credentials

DVC Studio is a web-based interface that allows you to share your machine learning projects with your team. To set up DVC Studio, follow the steps outlined in this [guide](https://dvc.org/doc/studio/user-guide/experiments/create-a-project). After the setup, when checking the project summary, you may see missing metrics. This is because the metrics are tracked by DVC and are located in remote storage instead of GitHub.

![Imgur](https://i.imgur.com/nfRhG5I.png)

To allow DVC Studio to access the metrics, you need to set up credentials. First, navigate to the `Settings` tab of the project and click on the `Data remotes / cloud storage credentials` section. Then, add new credentials for the remote storage. For example, if you are using AWS S3, the credentials should have read access to the S3 buckets.

![Imgur](https://i.imgur.com/EstJaJ9.png)

### Automatically pushing your experiments to DVC Studio

To enable automatic pushing of your experiments to DVC Studio, use the following command to log in from your console:

```bash
dvc studio login
```

Once you rerun your experiments as outlined in the previous section, you can view the results in DVC Studio.

![Imgur](https://i.imgur.com/tWux5Uy.png)

## Managing ML model lifecycle with DVC Studio

After being trained with several experiments, a model can be matured and registered in stages such as `dev` for review or `production` for deployment. However, the journey does not end after deployment. The model must be monitored and retrained to prevent degradation. In this section, we will explore how to manage the ML model lifecycle with DVC Studio.

![Imgur](https://imgur.com/Oclbw7T.jpg)

### Registering your model with a new version

First, navigate to the `Models` tab where you will see the `house-price-predictor-model` as defined in the `dvc.yaml` file. Click `Register`, enter a version number, and then click `Register version` in the pop-up window.

Registration will automatically create an annotated Git tag in the linked GitHub repository. You can view the tag in the `Code` tab of the repository. This makes it easy to track versions using the tags in the future.

![Imgur](https://i.imgur.com/M9bmq5Z.png)

### Moving your model to a stage

After registering the model, you can assign it to a stage. Click the `Assign stage` button and name the stage `dev`. Once the stage is assigned, a new tag is automatically created in the GitHub repository to reflect the stage.


![Imgur](https://i.imgur.com/4ymCIeS.png)

### Setting up GitHub Actions for deployment

In the following scenario, we will move the model to the `prod` stage, simulating its deployment. We will use GitHub Actions to emulate the deployment process. To enable this, you need to add an access token to the GitHub repository, allowing GitHub Actions to access the DVC remote storage.

Go to the `Settings` tab of the project and add the DVC Studio access token to the GitHub repository secrets with the name `DVC_STUDIO_TOKEN`. The process is illustrated in the screenshot below.

![Imgur](https://i.imgur.com/Mx1Jyxx.png)

You can find a template GitHub Action workflow in the `.github` folder of the project. Essentially, this workflow triggers on every tag creation event and checks if the stage is `prod`. If the stage is `prod`, it will download the model from remote storage and deploy it (in this example, no actual deployment occurs; only a message is printed). For a detailed explanation of this workflow, see [here](https://dvc.org/doc/start/model-registry/model-cicd?tab=GitHub#detailed-explanation-of-the-cicd-templates).

### Deploying the model

Now, move the model to the `prod` stage as before. After doing so, you should see that a GitHub Actions workflow is triggered and the printed message appears in the log.

![Imgur](https://i.imgur.com/grvRJk4.png)

You can then repeat the above steps to create a new version of the model and assign it to different stages to manage the ML model lifecycle.
