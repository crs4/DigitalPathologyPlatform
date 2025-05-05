---
layout: default
title: Execute workflows
parent: Usage
nav_order: 1
---

## Prerequisites

This workflow version supports only Whole-Slide Images (WSIs) in the [MIRAX format](https://openslide.org/formats/mirax/){:target="_blank"}. It is specifically tailored for prostate cancer needle biopsies stained with hematoxylin and eosin (H&E).

If you do not have access to suitable WSIs, you can use slides from an open dataset provided by the *Department of Information Technology and SciLifeLab, Uppsala University* and the *Department of Medical Biosciences, Pathology, Umeå University*. This dataset is described in the following publication:

**Chelebian, E., Avenel, C., Järemo, H., Andersson, P., Wählby, C., & Bergh, A.** (2025). *A clinical prostate biopsy dataset with undetected cancer*. Scientific Data, 12(1), 423.  
[![DOI:10.1038/s41597-025-04758-7](https://zenodo.org/badge/DOI/10.1038/s41597-025-04758-7.svg)](https://doi.org/10.1038/s41597-025-04758-7){:target="_blank"}

You can download the dataset from [![DOI:10.57804/epa0-8v59](https://zenodo.org/badge/DOI/10.57804/epa0-8v59.svg)](https://doi.org/10.57804/epa0-8v59){:target="_blank"}

To be imported within the platform, slides names must adhere to the following pattern:

`<case_id>-<slide_index>[.<ext>]`

Since the slides in this dataset use a different naming convention, we provide a helper tool to rename and organize the files into a compatible format.  
To rename the slides, follow these steps:

```bash
git clone https://gist.github.com/6ea4d6c0d0a07e8486c6c1613051c03a.git rename_slides
cd rename_slides
python rename_umea_dataset.py <SLIDES_INPUT_DIR> <SLIDES_OUTPUT_DIR>
```

where `SLIDES_INPUT_DIR` is the path to the original dataset slides, and `SLIDES_OUTPUT_DIR` is the destination directory where the renamed slides will be copied, conforming to the standard platform naming convention.  
To move (instead of copy) the slides, add the `--move` option:

`python rename_umea_dataset.py --move <SLIDES_INPUT_DIR> <SLIDES_OUTPUT_DIR>`

To facilitate the process, we suggest to use the `$INPUT_DIR` directory defined in the `.env` file as `SLIDE_OUTPUT_DIR`.

## Execute workflows

After starting the platform services (using `./compose.sh`), place the WSIs to be analyzed in the `$INPUT_DIR` directory, which is defined in your `.env` file.

Use `slide_importer/local.py` to run either:
- the `basic_pipeline` for slide ingestion and tissue segmentation (H&E WSIs), or
- the more advanced `pca_pipeline`, which also performs prostate cancer classification.

```bash
cd slide-importer
poetry install
poetry run python slide_importer/local.py basic_pipeline  --user $AIRFLOW_USER -P $AIRFLOW_PASSWORD --server-url http://localhost:$AIRFLOW_WEBSERVER_PORT  --wait --params '{"level": 8}'
# or 
poetry run python slide_importer/local.py pca_pipeline --user $AIRFLOW_USER -P $AIRFLOW_PASSWORD --server-url http://localhost:$AIRFLOW_WEBSERVER_PORT -p '{ "tissue-high-level": 8, "tissue-high-filter": "tissue_low>1", "tumor-filter": "tissue_low>1", "gpu": null}'  --wait 
```

Parameters for the 'basic_pipeline' are defined in `cwl/tissue_segmentation_workflow.cwl`, while the ones for the 'pca_pipeline' are defined in `cwl/pca_classification_workflow.cwl`.
