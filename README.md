# CRS4 Digital Pathology Platform
The Digital Pathology platform developed by CRS4 is a web-based application tailored for interactive annotation of Whole Slide Images in the context of clinical research. It is a multi-component system that integrates [OME Remote Objects (OMERO)](https://www.openmicroscopy.org/omero/), thought the integration of the [ome_seadragon plugin](https://github.com/crs4/ome_seadragon), with a system for annotating tumour tissues, developed entirely at CRS4. 
The platform was born out of a collaboration with the Karolinska Institutet in Stockholm in the context of the [ProMort](https://academic.oup.com/aje/article/188/6/1165/5320054?login=true) project, where it allowed pathologists to annotate thousands of prostate tissue images.  Its development has continued, incorporating several new functionalities.  Most recently, the ability to apply deep learning models to images for detecting tumour regions in prostate biopsies and for classifying their severity was added (in the [DeepHealth](https://deephealth-project.eu/) project).  The use of the platform for the study of prostate cancer has also been [validated in a collaborative study by CRS4 and KI](https://www.nature.com/articles/s41598-021-82911-z).

## Docker images

* Django based web server: https://hub.docker.com/repository/docker/crs4/promort-web
* Nginx server with static files: https://hub.docker.com/repository/docker/crs4/promort-nginx
