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

To install the `bargal` package run:

```bash
pip install git+https://github.com/ludanortmun/itesm-mna-barred-galaxies.git
```

## Usage

### Classifying galaxies

#### Basic usage

The `bargal-classify` command can be used to detect bars in galaxies. As an argument, it requires a path to the dataset,
which can be in CSV or FITS format. This dataset must contain at least the `name`, `objra` and `objdec` columns.

By default, this will write a report to the `./report_{timestamp}.csv` path, where `{timestamp}` will be replaced with 
the timestamp at which the report was written. It can be overridden with the `-o | --output-path` option.

```bash
bargal-classify data/dataset.csv -o output/directory/report.csv
```

This report will be the same as the original dataset with an additional column `is_barred_pred`, which will be 1 if the
galaxy is barred or 0 otherwise.

This command will use the dataset to retrieve and download the corresponding images for each galaxy directly from
Legacy Survey. It is possible to provide a path to a local directory by passing the `--img-dir` option,
in which case the following should happen:

- If the local directory contains an image for the given galaxy, it will use that instead of downloading a new one.
- If an image is not found locally, an image will be downloaded and stored in the given directory.
- The report will include a new `img` column that will include the local path to the .fits image.

```bash
bargal-classify data/dataset.csv -o output/directory/report.csv --img-dir path/to/img/dir
```

`--skip` (`-s`) and `--top` (`-t`) parameters can also be used to classify only a subset of the dataset. This is useful
to implement pagination logic to the classification jobs. If any of them are present, the resulting report will only
include the processed rows.

```bash
bargal-classify data/dataset.csv -o output/directory/report.csv --skip 10 --top 10
```

The `--print-report` flag can also be added, in which case the command will print the results in addition to writing 
them to the report file. This is recommended for smaller outputs.

```bash
bargal-classify data/dataset.csv --top 10 --print-report
```

#### Model selection

The `--model` option can be passed to select which model to use for classification. At the time being, only the `mlp`
option is available, which will select the baseline MLP classifier. Details on this model can be found in
[this notebook](https://github.com/ludanortmun/itesm-mna-barred-galaxies/blob/main/notebooks/Avance3.Equipo22.ipynb).

```bash
bargal-classify data/dataset.csv -o output/directory/report.csv --model mlp
```

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

The `bargal-preprocess` command is used to preprocess the downloaded images. The main purpose of this is to create the
dataset to train the classifier model with. This is intended to be used with FITS images.
It requires the path to the dataset and the path to the downloaded images' folder. By default, the output images will be
saved in the data/preprocessed directory, but can be changes using the `--output-dir` (`-o`) option.

```bash
bargal-preprocess data/dataset.csv data/images -o data/preprocessed
````

This command also has skip and top parameters to limit the number of images to be preprocessed.

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
You can do this by installing the package from Git. To do this, run the following command in a code cell:

``` 
!pip install git+https://github.com/ludanortmun/itesm-mna-barred-galaxies.git
```

You will be prompted to restart your session. After you do, the bargal package should be available for import.

Then, replace any path referencing the `../data` directory to match the path to the data in your Colab session. 
