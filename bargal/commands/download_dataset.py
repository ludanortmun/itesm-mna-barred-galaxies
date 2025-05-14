import os

import click
import pandas as pd

from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy
from bargal.dataset.load import load_dataset


@click.command()
@click.argument('dataset_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory for downloaded images')
@click.option('--skip', '-s', type=int, default=None, help='Number of images to skip')
@click.option('--top', '-t', type=int, default=None, help='Number of images to download')
@click.option("--by-bands", is_flag=True,
              help="Will download images for each band separately, in addition to the RGB image. "
                   "This is only available for JPG downloads.")
@click.option("--use-fits", is_flag=True,
              help="Will download images in FITS format instead of JPG. If true, --by-bands will be ignored.")
def main(dataset_file: str, output_dir: str, skip: int or None, top: int or None, by_bands: bool = False,
         use_fits: bool = False) -> None:
    """Download images for galaxies listed in a CSV or FITS file."""
    df = load_dataset(dataset_file)

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    client = GalaxyImageClient(storage_path=output_dir)

    start = skip if skip else 0
    end = min(start + top if top else len(df), len(df))

    failures = []

    for i in range(start, end):
        row = df.iloc[i]
        g = Galaxy.from_dict(row.to_dict())

        success = _attempt_download(client, g, by_bands, use_fits)

        if not success:
            failures.append(g)
            click.echo(f"Failed to download image for {g.name}")

    retry_count = 0
    while len(failures) > 0 and retry_count < 3:
        click.echo(f"Retrying {len(failures)} failed downloads...")
        retry_count += 1
        new_failures = []

        for g in failures:
            success = _attempt_download(client, g, by_bands, use_fits)

            if not success:
                new_failures.append(g)
                click.echo(f"Failed to download image for {g.name} on retry {retry_count}")

        failures = new_failures

    if len(failures) > 0:
        click.echo(f"Failed to download images for {len(failures)} galaxies after {retry_count} retries.")
        for g in failures:
            click.echo(f"Failed galaxy: {g.name}")


def _attempt_download(client: GalaxyImageClient, g: Galaxy, by_bands: bool, use_fits: bool) -> bool:
    try:
        if use_fits:
            # FITS images are only available when downloading as an observation.
            client.get_as_observation(g, save_to_disk=True, use_fits=True)
        else:
            client.get_image(g, save_to_disk=True)
            if by_bands:
                client.get_image_as_bands(g, save_to_disk=True, bands='grz')
    except Exception as e:
        click.echo(f"Failed to download image for {g.name}: {e}")
        return False

    return True


if __name__ == '__main__':
    main()
