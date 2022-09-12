# OpenDDM 

[![GitHub](https://img.shields.io/github/license/koenderinklab/ddmPilotCode?)](https://github.com/koenderinklab/ddmPilotCode/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/koenderinklab/ddmPilotCode/branch/master/graph/badge.svg?token=V4VZcNYyMG)](https://codecov.io/gh/koenderinklab/ddmPilotCode)
![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/koenderinklab/ddmPilotCode/deploy-documentation?label=documentation)
![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/koenderinklab/ddmPilotCode/Build%20and%20test%20Python%20package)
![GitHub repo size](https://img.shields.io/github/repo-size/koenderinklab/ddmPilotCode)


A Python package to analyse an image sequence and measure diffusion properties through Fourier techniques.

**This package is under active development and currently in a pre-alpha state.**

Additional information as well as API references can be found on our [webpage](https://koenderinklab.github.io/ddmPilotCode/).

## Installation for users

### Required dependencies
- Python 3.8 or 3.9
- Anaconda (recommended)
- Optional: Nvidia CUDA GPU

### Instructions
OpenDDM is under development and not (yet) available through PyPI. We recommend installing the package in a conda environment. To install the software locally:

```bash
conda env create -n ddm_env python=3.8
conda activate ddm_env
pip install git+https://github.com/koenderinklab/ddmPilotCode
```

In order to make use of a CUDA-enabled GPU with cupy, you can install the additional dependencies with

```bash
# conda env create -n ddm_env python=3.8
# conda activate ddm_env
pip install git+https://github.com/koenderinklab/ddmPilotCode#egg=ddm[cuda]
```

Please look at the [CuPy requirements](https://docs.cupy.dev/en/stable/install.html) for more info on suitable GPUs.

## Installation for developers

```bash
git clone git@github.com:koenderinklab/ddmPilotCode.git ddm
cd ddm
conda env create -f environment.yml
conda activate ddm_env
pip install -e .[dev]
``` 

### Running tests

To run the test suite after installing OpenDDM with the development depednencies, run `pytest` in the root directory of the openddm repository.

## License
Copyright 2022 Technische Universiteit Delft

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
