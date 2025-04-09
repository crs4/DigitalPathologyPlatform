---
layout: default
title: Welcome
nav_order: 1
---

# Welcome to CRS4 Digital Pathology Platform

This site provides documentation for the CRS4 Digital Pathology Platform (CDPP), an open-source system for managing whole slide image collections, structured annotation, and computational pathology workflows.

# Platform overview

The CRS4 Digital Pathology Platform (CDPP) is an open-source software system designed to support digital pathology research through:

- Structured, multi-label morphological and clinical image annotation
- Support for controlled, customizable annotation protocols
- Annotation tools that enhance accuracy, efficiency, and consistency
- Workflow-based computational analysis with provenance tracking

CDPP is based on a modular architecture comprising:

- A slide repository (based on <a href="https://www.openmicroscopy.org/omero/" target="_blank">Open Microscopy's OMERO</a>)
- A virtual microscope for WSI viewing <a href="https://github.com/crs4/ome_seadragon/tree/master" target="_blank">:octocat: View on Github</a>
- An annotation manager supporting both manual and AI-assisted annotation <a href="https://github.com/crs4/DigitalPathologyPlatform/tree/master" target="_blank">:octocat: View on Github</a>
- A workflow manager for automated image analysis (via Apache Airflow + CWL)

Its web-based interface supports distributed, protocol-driven collaboration and simplifies setup through Docker-based deployment.
