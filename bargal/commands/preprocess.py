import os

import click
import numpy as np
from PIL import Image

from bargal.dataset.load import load_dataset
from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy
from bargal.preprocessing import PREPROCESSORS, ImageProcessor


@click.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.argument('img_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='data/processed', type=click.Path(), help='Output directory for processed images')
@click.option('--skip', '-s', type=int, default=None, help='Number of entries to skip')
@click.option('--top', '-t', type=int, default=None, help='Number of entries to process')
@click.option('--preprocessor', '-p', type=click.Choice(PREPROCESSORS.keys(), case_sensitive=False), default='GRLOG_GR_DIFF', help='Preprocessor to use')
def preprocess(dataset_path: str,
               img_path: str,
               output_dir: str,
               skip: int or None,
               top: int or None,
               preprocessor: str) -> None:
    click.echo(f'Loading dataset from {dataset_path}'"")
    df = load_dataset(dataset_path)

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    click.echo(f"Loading images from {img_path}")
    client = GalaxyImageClient(storage_path=img_path)

    start = skip if skip else 0
    end = min(start + top if top else len(df), len(df))

    click.echo(f'Using preprocessor: {preprocessor.upper()}')
    click.echo(f"Processed images will be saved to {output_dir}")
    img_processor = PREPROCESSORS[preprocessor.upper()]

    for i in range(start, end):
        row = df.iloc[i]
        g = Galaxy.from_dict(row.to_dict())

        processed_image = _get_and_process_image(g, client=client, img_processor=img_processor)
        _save_image(processed_image, output_dir, g.name)


def _get_and_process_image(galaxy: Galaxy, *, client: GalaxyImageClient, img_processor: ImageProcessor) -> np.ndarray:
    """
    Downloads and processes the image for a given galaxy.

    Args:
        galaxy (Galaxy): The galaxy object.
        client (GalaxyImageClient): The image client to download images.
        img_processor (ImageProcessor): The image processor to apply.

    Returns:
        np.ndarray: The processed image array.
    """
    observation = client.get_as_observation(galaxy, save_to_disk=True, use_fits=True, skip_rgb=True)
    return (img_processor.preprocess(observation)*255).astype(np.uint8)

def _save_image(img: np.ndarray, output_dir: str, name: str) -> None:
    """
    Saves the processed image to the specified directory.

    Args:
        img (np.ndarray): The processed image array.
        output_dir (str): The output directory to save the image.
        name (str): The name of the galaxy.
    """
    processed_image_name = f"{output_dir}/{name}.png"
    with Image.fromarray(img, 'L') as img:
        img.save(processed_image_name)

if __name__ == "__main__":
    preprocess()
