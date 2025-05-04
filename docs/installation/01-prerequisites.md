---
layout: default
title: Prerequisites
parent: Installation & Usage
nav_order: 1
---

## Prerequisites

Before getting started, ensure the following software is installed on your system:

- [Docker](https://www.docker.com){:target="_blank"} (version 26.1 or higher)
- [Docker Compose](https://docs.docker.com/compose/){:target="_blank"} (version 2.33 or higher)
- [Git](https://git-scm.com){:target="_blank"}
- [Poetry](https://python-poetry.org/){:target="_blank"} (tested with version 1.8.3)

Your system should support virtualization and have sufficient resources. **At least 16 GB of RAM is recommended** for optimal performance.

To run the default tissue detection pipeline, it is **strongly recommended** to have an NVIDIA GPU compatible with the [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit){:target="_blank"} (version 11.3.1 or higher).
To run the cancer classification pipeline, **a compatible NVIDIA GPU is required**.
