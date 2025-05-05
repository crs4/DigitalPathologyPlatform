---
layout: default
title: Execute workflows
parent: Usage
nav_order: 1
---

# Execute workflows

Once the platform services are up and running (via ```./compose.sh```), put some data in the $INPUT_DIR directory (variable defined in your .env file). For testing purpose, as input you can use these MIRAX [slides](https://researchdata.se/en/catalogue/dataset/2024-144).

You can use ```slide_importer/local.py``` for running the *basic_pipeline* , i.e. the slide ingestion and the tissue segmentation (for H&E WSIs), or the more complex *pca_pipeline*, which classifies prostate cancer in addition to the tissue segmentation.

```bash
cd slide-importer
poetry install
poetry run python slide_importer/local.py basic_pipeline  --user $AIRFLOW_USER -P $AIRFLOW_PASSWORD --server-url http://localhost:$AIRFLOW_WEBSERVER_PORT  --wait --params '{"level": 8}'
# or 
poetry run python slide_importer/local.py pca_pipeline --user $AIRFLOW_USER -P $AIRFLOW_PASSWORD --server-url http://localhost:$AIRFLOW_WEBSERVER_PORT -p '{ "tissue-high-level": 8, "tissue-high-filter": "tissue_low>1", "tumor-filter": "tissue_low>1", "gpu": null}'  --wait 
```

Parameters for the *basic_pipeline* are defined in ```cwl/tissue_segmentation_workflow.cwl```, while the ones for the *pca_pipeline* are defined in ```cwl/pca_classification_workflow.cwl```.

# Extending workflows
First, It is strongly suggested to read the documentation of [Apache Airflow](https://airflow.apache.org/). Consider also that the Python module ```data/dags/utils.py``` contains many useful functions.

The easiest way for developing a custom workflow is to copy the ```data/dags/basic_pipeline.py``` on another file, under the *dags* directory. It is suggested to create the custom processing as a *CWL* file, under the directory ```./cwl```. You have to create a Python companion file under the ```dags``` directory, see the ```*_cwl.py``` files as an example. For executing the right *CWL*, you have to call the ```processing function``` (defined in ```data/dags/utils.py```) with the dag id defined in the Python companion file. 

For uploading output to the CDPP, in general you have to upload first to OMERO. Take a look at *add_prediction_to_omero* and *add_prediction_to_promort* functions.
For creating vectorial shapes, take a look at the *tissue_branch*  function. For making visual predictions as heatmaps, see *tumor_branch*. 
