## Install Miniconda

**This step is only necessary if you don't have conda installed already**:

- download the Miniconda installer for your operating system (Windows, MacOSX
  or Linux) [here](https://docs.conda.io/en/latest/miniconda.html)
- run the installer following the instructions
  [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)
  depending on your operating system.

## Create conda environment

```sh
# Clone this repo
git clone https://github.com/HieuMagic/DS_Predictor
cd DS_Predictor
# Create a conda environment with the required packages for this project:
conda env create -f environment.yml
```

## Check your install

To make sure you have all the necessary packages installed, we **strongly
recommend** you to execute the `check_env.py` script located at the root of
this repository:

```sh
# Activate your conda environment
conda activate ds
python check_env.py
```

Make sure that there is no `FAIL` in the output when running the `check_env.py`
script, i.e. that its output looks similar to this:

```
Using python in /home/hieumagic/.conda/envs/ds
3.13.0 | packaged by conda-forge | (main, Nov 27 2024, 19:18:50) [GCC 13.3.0]

[ OK ] numpy version 2.3.4
[ OK ] scipy version 1.16.2
[ OK ] matplotlib version 3.10.7
[ OK ] sklearn version 1.7.2
[ OK ] pandas version 2.3.3
[ OK ] seaborn version 0.13.2
[ OK ] notebook version 7.4.7
[ OK ] plotly version 6.3.1
[ OK ] requests version 2.32.5
[ OK ] playwright installed (version check skipped)
[ OK ] scrapy version 2.13.3
[ OK ] lxml version 5.4.0
[ OK ] trafilatura version 2.0.0
[ OK ] bs4 version 4.14.2
```

## Run Jupyter notebooks locally

```sh
# Activate your conda environment
conda activate ds
jupyter notebook full-index.ipynb
```

`full-index.ipynb` is an index file helping to navigate the notebooks.
All the Jupyter notebooks are located in the `notebooks` folder.
