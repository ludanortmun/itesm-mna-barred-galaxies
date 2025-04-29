# Barred Galaxies Dataset Tool

A Python tool for downloading and managing galaxy images from the Legacy Survey DR10, specifically focused on barred
galaxies' analysis.

## Installing dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Installation

All scripts and tools are contained in the `bargal` (short for **bar**red **gal**axies) package. This package contains
CLI applications to manage the dataset, as well as modules that are used as part of the implementation of the Jupyter
notebooks.

To install the `bargal` package, from the repository root run:

```bash
pip install .
```

## Usage

### Download images

The basic dataset is included in this repository; however, due to size constraints, the actual images are not included.
You can download the images using the `bargal-datasetdown` command.

To download galaxy images from a CSV dataset, run the following command:

```bash
bargal-datasetdown data/dataset.csv -o output/directory
```

It is recommended to use `data/images` as the output directory.

### Notebooks

The Jupyter notebooks in the `notebooks` directory are designed to help you analyze the downloaded images. If the
`bargal` package is installed, you can import any of the modules directly in the notebooks.