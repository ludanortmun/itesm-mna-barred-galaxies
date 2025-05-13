import pandas as pd
from astropy.io import fits
import os


def load_dataset(filename: str) -> pd.DataFrame:
    """
    Load a dataset based on its file extension.

    Args:
        filename (str): Path to the file.

    Returns:
        pd.DataFrame: DataFrame containing the file data.

    Raises:
        ValueError: If the file format is unsupported.
    """
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext == '.fits':
        return load_fits(filename)
    elif ext == '.csv':
        return load_csv(filename)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def load_fits(filename: str) -> pd.DataFrame:
    """
    Load a FITS file and return its contents as a pandas DataFrame.

    Args:
        filename (str): Path to the FITS file.

    Returns:
        pd.DataFrame: DataFrame containing the FITS data.
    """
    hdulist = fits.open(filename)
    tbdata = hdulist[1].data
    name = tbdata.field('name')
    ra = tbdata.field('objra')
    dec = tbdata.field('objdec')
    bars = tbdata.field('Bars')

    # Convert to DataFrame
    return pd.DataFrame({
        'name': name,
        'objra': ra,
        'objdec': dec,
        'Bars': bars
    })


def load_csv(filename: str) -> pd.DataFrame:
    """
    Load a CSV file and return its contents as a pandas DataFrame.

    Args:
        filename (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.
    """
    df = pd.read_csv(filename)
    return df
