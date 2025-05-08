---
layout: default
title: Review worklist creation
parent: Usage
nav_order: 2
---

## Creating the review worklist

Once one or more reviewers have been created, you can generate review worklists to begin reviewing Whole-Slide Images.
This requires assigning ROI and clinical annotation tasks to existing reviewers using the Annotation Manager's administration tools.

### ROIs annotation

To create the ROI annotation worklist, run the `python manage.py build_rois_reviews_worklist` command. By default, the command assigns all existing cases to all reviewers in the `ROIS_MANAGERS` group using a round-robin strategy.

```bash
user@host:~/cdpp-workflows$ ./compose.sh exec promort-web python manage.py build_rois_reviews_worklist
WARN[0000] The "CWLDOCKER_ENV" variable is not set. Defaulting to a blank string.
...
INFO === Starting ROIs worklist creation ===
INFO Creating RANDOM worklist
INFO Processing case P_003
INFO No ROIs Annotation found, creating a new one
INFO Saved new ROIs Annotation with label 782b19dba74440d797f6bbf069f2d8c4 and assigned to test_reviewer
INFO Processing slide P_003-ABC
INFO Creating steps for ROIs Annotation 782b19dba74440d797f6bbf069f2d8c4
INFO Produced label 782b19dba74440d797f6bbf069f2d8c4-ABC
INFO Saved new ROIs Annotation Step with label 782b19dba74440d797f6bbf069f2d8c4-ABC
INFO Processing slide P_003-DEF
INFO Creating steps for ROIs Annotation 782b19dba74440d797f6bbf069f2d8c4
INFO Produced label 782b19dba74440d797f6bbf069f2d8c4-DEF
INFO Saved new ROIs Annotation Step with label 782b19dba74440d797f6bbf069f2d8c4-DEF
INFO Processing case P_001
INFO No ROIs Annotation found, creating a new one
INFO Saved new ROIs Annotation with label cf0e125804664b839e007386220f34d0 and assigned to test_reviewer
INFO Processing slide P_001-DEF
INFO Creating steps for ROIs Annotation cf0e125804664b839e007386220f34d0
INFO Produced label cf0e125804664b839e007386220f34d0-DEF
INFO Saved new ROIs Annotation Step with label cf0e125804664b839e007386220f34d0-DEF
INFO Processing slide P_001-ABC
INFO Creating steps for ROIs Annotation cf0e125804664b839e007386220f34d0
INFO Produced label cf0e125804664b839e007386220f34d0-ABC
INFO Saved new ROIs Annotation Step with label cf0e125804664b839e007386220f34d0-ABC
INFO === ROIs worklist creation completed ===
```

### Clinical annotation

Once the ROI review worklists have been created, you can generate clinical annotation review worklists by running the `python manage.py build_clinical_reviews_worklist` command. By default, a clinical annotation request is created for each ROI annotation and assigned to the same reviewer. To assign additional reviewers, use the `--reviewers-count` option followed by the desired number. These additional reviewers are selected from the `CLINICAL_MANAGERS` group. All ROIs generated during the linked ROI annotation step will be available for review by any user assigned a clinical annotation review linked to that specific step.

```bash
user@host:~/cdpp-workflows$ ./compose.sh exec promort-web python manage.py build_clinical_reviews_worklist
WARN[0000] The "CWLDOCKER_ENV" variable is not set. Defaulting to a blank string.
...
INFO === Starting clinical annotations worklist creation ===
INFO Processing ROIs Annotation 782b19dba74440d797f6bbf069f2d8c4
INFO Assigning review to user test_reviewer
INFO Saved Clinical Annotation with label 782b19dba74440d797f6bbf069f2d8c4
INFO Saved new Clinical Annotation Step with label 782b19dba74440d797f6bbf069f2d8c4-ABC
INFO Saved new Clinical Annotation Step with label 782b19dba74440d797f6bbf069f2d8c4-DEF
INFO Processing ROIs Annotation cf0e125804664b839e007386220f34d0
INFO Assigning review to user test_reviewer
INFO Saved Clinical Annotation with label cf0e125804664b839e007386220f34d0
INFO Saved new Clinical Annotation Step with label cf0e125804664b839e007386220f34d0-DEF
INFO Saved new Clinical Annotation Step with label cf0e125804664b839e007386220f34d0-ABC
INFO === Clinical annotation worklist creation completed ===
```

### Apply pipeline results

If the automatic annotation pipeline has been run on the slides to be reviewed, the regions detected by AI tools can be used as ROIs and included in the review process. To do this, run the command `python manage.py tissue_to_rois`. This will register the H&E-stained tissue regions detected by the pipeline tools as `Slice` and `Core` objects. To distinguish these ROIs from those manually created by reviewers, we recommend marking them explicitly as created by the default workflow manager user by passing `--username $PROMORT_USER` to the script.

```bash
user@host:~/cdpp-workflows$ ./compose.sh exec promort-web python manage.py tissue_to_rois --username $PROMORT_USER
WARN[0000] The "CWLDOCKER_ENV" variable is not set. Defaulting to a blank string.
...
INFO == Starting import job ==
INFO Loaded 4 ROIs annotation steps
INFO Processing ROIs annotation step 782b19dba74440d797f6bbf069f2d8c4-ABC
INFO Loading bounds for slide P_003-ABC
INFO response.status_code 200
INFO Slice saved with ID 1
INFO Loading core 1 of 5
INFO Core saved with ID 1
INFO Loading core 2 of 5
INFO Core saved with ID 2
...
INFO Loading core 2 of 2
INFO Core saved with ID 20
INFO Processing ROIs annotation step 782b19dba74440d797f6bbf069f2d8c4-DEF
INFO Loading bounds for slide P_003-DEF
INFO response.status_code 200
INFO Slice saved with ID 8
INFO Loading core 1 of 3
INFO Core saved with ID 21
INFO Loading core 2 of 3
INFO Core saved with ID 22
...
INFO Loading core 4 of 4
INFO Core saved with ID 41
INFO Processing ROIs annotation step cf0e125804664b839e007386220f34d0-DEF
INFO Loading bounds for slide P_001-DEF
INFO response.status_code 200
INFO Slice saved with ID 16
INFO Loading core 1 of 2
INFO Core saved with ID 42
INFO Loading core 2 of 2
...
INFO Loading core 2 of 2
INFO Core saved with ID 59
INFO Processing ROIs annotation step cf0e125804664b839e007386220f34d0-ABC
INFO Loading bounds for slide P_001-ABC
INFO response.status_code 200
INFO Slice saved with ID 24
INFO Loading core 1 of 2
INFO Core saved with ID 60
INFO Loading core 2 of 2
INFO Core saved with ID 61
...
INFO Loading core 1 of 1
INFO Core saved with ID 77
INFO == Job completed ==
```
