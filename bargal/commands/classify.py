import time

import click
import numpy as np

from pathlib import Path

from bargal.dataset.load import load_dataset
from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy
from bargal.predictors.baseline.predictor import MLPBaselinePredictor

SUPPORTED_MODELS = {
    'mlp': MLPBaselinePredictor,
}


@click.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--img-dir', type=click.Path(), default=None,
              help='Path to local image directory. If provided, galaxy images will be attempted to be loaded from it. '
                   'If a directory is not provided or an image is not found in it, it will instead download from Legacy Survey.')
@click.option('--output-path', '-o', default=None, type=click.Path(),
              help='Output path for the classification report.')
@click.option('--skip', '-s', type=int, default=None, help='Number of entries to skip')
@click.option('--top', '-t', type=int, default=None, help='Number of entries to process')
@click.option('--model', type=click.Choice(SUPPORTED_MODELS.keys(), case_sensitive=False), default='mlp',
              help='Model to use for classification.')
@click.option('--print-report', is_flag=True, default=False, help='Print the classification report.')
def main(dataset_path, img_dir, output_path, skip, top, model, print_report):
    click.echo(f'Loading dataset from {dataset_path}')
    df = load_dataset(dataset_path)

    if img_dir is not None:
        click.echo(f"Loading images from {img_dir}")
    else:
        click.echo("Image directory not specified, will download all images from Legacy Survey.")
    client = GalaxyImageClient(storage_path=img_dir)

    classifier_type = SUPPORTED_MODELS[model]
    classifier = classifier_type(img_client=client)

    df['is_barred_pred'] = np.nan
    if img_dir is not None:
        df['img'] = None

    start = skip if skip else 0
    end = min(start + top if top else len(df), len(df))

    for i in range(start, end):
        row = df.iloc[i]
        g = Galaxy.from_dict(row.to_dict())

        result = classifier.classify(g)
        df.at[i, 'is_barred_pred'] = int(result)

        if img_dir is not None:
            img_path = Path(img_dir) / Path(g.name.strip() + '.fits')
            df.at[i, 'img'] = str(img_path)


    report_path = None
    if output_path is None:
        report_path = Path(".") / Path(f'report_{time.strftime("%Y%m%d%H%M%S")}.csv')
    else:
        report_path = Path(output_path)
        report_dir = report_path.parent
        report_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Writing report to {report_path}")
    df.iloc[start:end].to_csv(report_path, index=False)

    if print_report:
        click.echo('Classification report')
        click.echo(df.iloc[start:end].to_markdown())


if __name__ == '__main__':
    main()
