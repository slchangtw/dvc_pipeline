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

DVC Studio is a web-based interface that allows you to share your machine learning projects with your team. To set up DVC Studio, follow the steps outlined in this [guide](https://dvc.org/doc/studio/user-guide/experiments/create-a-project). After the setup, when checking the summary of the project, you may see missing metrics since the metrics are tracked by DVC, therefore they are located in remote storgage instead of Github. 

![Imgur](https://i.imgur.com/nfRhG5I.png)


To allow DVC Studio to access the metrics, you have to set up credentials for DVC Studio to access the metrics. First, navigate to the `Settings` tab of the project, and click `Data remotes / cloud storage credentials` section and add new credentials for the remote storage. Since we use AWS S3 as an example, the credentials should able to read S3 buckets.

![Imgur](https://i.imgur.com/EstJaJ9.png)


To allow your experiments to be automatically pushed to DVC Studio, you have to log in to DVC Studio from your console using the command below:

```bash
dvc studio login
```

After rerunning your experiments as described in the previous section, you can view the results in DVC Studio.

![Imgur](https://i.imgur.com/tWux5Uy.png)

## Managing ML model lifecycle with DVC Studio

Being trained with several experiments, a model would be matured enough and can be registered in stages such as `dev` for reviewing or `production` for deployment. After deploying the model, the jouney does not end here since the model needs to be monitored and retrained to avoid model degradation. In this section, we will see how to manage the ML model lifecycle with DVC Studio.

![Imgur](https://imgur.com/Oclbw7T.jpg)

### Registering your model with a new version

Firstly, navigate to the `Models` tab, you can see `house-price-predictor-model` as we defined in the `dvc.yaml` file. Click `Register` and enter a version number and click `Register version` in the pop-up window.

The registration will automatically create a annotated Git tag to the linked GitHub repository. You can check the tag in the `Code` tab of the repository. So, in the future, you can easily track version by using the tags.

![Imgur](https://i.imgur.com/M9bmq5Z.png)

### Moving your model to a stage

After registering the model, you can move it to a stage. Click the `Assign stage` button and name the stage `dev`. After assigning the stage, a new tag is also created in the GitHub repository to indicate the stage.

![Imgur](https://i.imgur.com/4ymCIeS.png)

### Setting up GitHub Actions for deployment

In the following scenario, we will move the model to the `prod` stage and you can imagine the model will be deployed. We will use GitHub Actions to emulate the deployment process. To do that, we have to add an access token to the GitHub repository so that GitHub Actions can access the DVC remote storage.

Navigate to the `Settings` tab of the project, and copy-paste the DVC Studio access token to the GitHub repository secrets, with the name `DVC_STUDIO_TOKEN`. You can see the flow as the screenshot below.

![Imgur](https://i.imgur.com/Mx1Jyxx.png)

You can see a template Github Action workflow included in in the `.github` folder in the project. In a nutshell, the flow checks every tag creation event and see if the stage is `prod`. If so, the flow will download the model from the remote storage and deploy it (in this example, no deployment is done, just a message is printed). You can check a full explanation of this flow [here](https://dvc.org/doc/start/model-registry/model-cicd?tab=GitHub#detailed-explanation-of-the-cicd-templates).

### Deploying the model

Now you can move the model to the `prod` stage as we did before. After that, you can see a GitHub Actions workflow is triggered and the printed message in the log.

![Imgur](https://i.imgur.com/grvRJk4.png)

You can then repeat the above-mentioned steps create a new version of the model, assign it to the different stages to manage the ML model lifecycle.