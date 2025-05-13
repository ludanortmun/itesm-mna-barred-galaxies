import os

import click
import numpy as np
from PIL import Image

from bargal.dataset.load import load_dataset
from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy
from bargal.preprocessing import GRLOG_GR_DIFF


@click.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.argument('img_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='data/processed', type=click.Path(), help='Output directory for processed images')
@click.option('--skip', '-s', type=int, default=None, help='Number of entries to skip')
@click.option('--top', '-t', type=int, default=None, help='Number of entries to process')
def preprocess(dataset_path: str,
               img_path: str,
               output_dir: str,
               skip: int or None,
               top: int or None) -> None:
    df = load_dataset(dataset_path)

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    client = GalaxyImageClient(storage_path=img_path)

    start = skip if skip else 0
    end = min(start + top if top else len(df), len(df))

    img_processor = GRLOG_GR_DIFF

    for i in range(start, end):
        row = df.iloc[i]
        g = Galaxy.from_dict(row.to_dict())
        observation = client.get_as_observation(g, save_to_disk=True, use_fits=True)

        processed_image = img_processor.preprocess(observation)
        processed_image = (processed_image * 255).astype(np.uint8)

        processed_image_name = f"{output_dir}/{g.name}_processed.png"
        img = Image.fromarray(processed_image, 'L')
        img.save(processed_image_name)


if __name__ == "__main__":
    preprocess()
