import os

import click
import pandas as pd

from bargal.images.client import GalaxyImageClient
from bargal.images.storage import ImageFileStore
from bargal.models import Galaxy


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory for downloaded images')
@click.option('--top', '-t', type=int, default=None, help='Number of images to download')
def main(csv_file: str, output_dir: str, top: None):
    """Download images for galaxies listed in a CSV file."""
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    storage = ImageFileStore(output_dir)
    client = GalaxyImageClient(local_dir=output_dir)

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        g = Galaxy.from_dict(row.to_dict())

        # Since we are using the client with local_dir, we can directly save the image
        client.get_image(g)

        if top is not None and index + 1 >= top:
            click.echo(f"Downloaded {top} images.")
            break


if __name__ == '__main__':
    main()
