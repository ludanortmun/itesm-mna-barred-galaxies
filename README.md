# Barred Galaxies Dataset Tool

A Python tool for detecting barred galaxies in astronomical images. Part of my Master's degree project at ITESM, in
collaboration with UNAM's Insituto de Astronomía.

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

To download galaxy images from a CSV or FITS dataset, run the following command:

```bash
bargal-datasetdown data/dataset.csv -o output/directory
```

It is recommended to use `data/images` as the output directory.

By adding the `--by-bands` flag, this command will also download individual images for each band.

```bash
bargal-datasetdown data/dataset.csv -o data/images --by-bands
```

It is also possible to use the `--skip` and `--top` options to limit the number of images downloaded. This is useful for
downloading a subset of the images for this dataset or for applying pagination logic to download images in batches.

For example, the following command will only download the first 10 records:

```bash
bargal-datasetdown data/dataset.csv -o data/images --by-bands --top 10
```

And then the following command will skip the first 10 records and download the next 10:

```bash
bargal-datasetdown data/dataset.csv -o data/images --by-bands --skip 10 --top 10
```

Additionally, you can use the `--use-fits` flag to download the images in FITS format instead of JPEG. This will ignore
the `--by-bands` flag, since FITS files contain all bands in a single file.

```bash
bargal-datasetdown data/dataset.csv -o data/images --use-fits
```

### Preprocess images

The `bargal-preprocess` command is used to preprocess the downloaded images. This is intended to be used with FITS
images.
It requires the path to the dataset and the path to the downloaded images' folder. By default, the output images will be
saved in the data/preprocessed directory, but can be changes using the `--output-dir` (`-o`) option.

```bash
bargal-preprocess data/dataset.csv data/images -o data/preprocessed
````

This command also skip and top parameters to limit the number of images to be preprocessed.

```bash
bargal-preprocess data/dataset.csv data/images -o data/preprocessed --skip 10 --top 10
```

By default, images will be processed using the GRLOG_GR_DIFF processor, which computes the difference between the G band
and the R band, applying a logarithmic transformation to the R band beforehand. This is the recommended processor for
this dataset. However, other processors are available and can be used by specifying the `--processor` (`-p`) option.

```bash
bargal-preprocess data/dataset.csv data/images -o data/preprocessed -p SQRLOG_GR_DIFF
```

For a list of registered processors, refer to: [bargal/preprocessing.py](bargal/preprocessing.py).

### Notebooks

The Jupyter notebooks in the `notebooks` directory are designed to help you analyze the downloaded images. If the
`bargal` package is installed, you can import any of the modules directly in the notebooks.

#### Running in Google Colab

To be able to run the notebooks in Google Colab, you need to ensure the `bargal` package is installable in your session.
You can do this by downloading this repository as a ZIP file and uploading it to your Google Colab session. To download
the latest revision of the main branch as a ZIP file, use this
URL: https://github.com/ludanortmun/itesm-mna-barred-galaxies/archive/refs/heads/main.zip

Then, at the start of the notebook, add and run a code cell with the following commands:

```
!unzip itesm-mna-barred-galaxies-main.zip
!pip install ./itesm-mna-barred-galaxies-main
```

This command will unzip the repository files and install the `bargal` package in your Google Colab session.

Then, replace any path referencing the `../data` directory with `/content/itesm-mna-barred-galaxies-main/data`. 