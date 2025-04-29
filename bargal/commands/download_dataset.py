import os

import click
import pandas as pd

from bargal.images.client import GalaxyImageClient
from bargal.images.storage import ImageFileStore
from bargal.models import Galaxy


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory for downloaded images')
@click.option('--skip', '-s', type=int, default=None, help='Number of images to skip')
@click.option('--top', '-t', type=int, default=None, help='Number of images to download')
def main(csv_file: str, output_dir: str, skip: int or None, top: int or None):
    """Download images for galaxies listed in a CSV file."""
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    storage = ImageFileStore(output_dir)
    client = GalaxyImageClient(local_dir=output_dir)

    start = skip if skip else 0
    end = min(start + top if top else len(df), len(df))

    for i in range(start, end):
        row = df.iloc[i]
        g = Galaxy.from_dict(row.to_dict())
        client.get_image(g)

if __name__ == '__main__':
    main()
