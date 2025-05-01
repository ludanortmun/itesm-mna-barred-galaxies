import click

from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy


@click.command()
@click.argument('ra', type=float)
@click.argument('dec', type=float)
@click.option('--name', '-n', help='Custom filename (without extension)')
@click.option("--by-bands", is_flag=True,
              help="Will download images for each band separately, in addition to the RGB image")
def main(ra: float, dec: float, name: str, by_bands: bool = False) -> None:
    """Download JPEG cutout from Legacy Survey using coordinates."""
    g = Galaxy(name, ra, dec)
    client = GalaxyImageClient()
    img_data = client.get_image(g, save_to_disk=False)

    filename = f"{g.name or f'cutout_ra{ra}_dec{dec}'}.jpg"
    with open(filename, 'wb') as f:
        f.write(img_data)
    click.echo(f"Image saved as {filename}")

    if by_bands:
        bands = client.get_image_as_bands(g, save_to_disk=False, bands='grz')
        for band, band_img in bands.items():
            _filename = f"{filename}.{band}.jpg"
            with open(_filename, 'wb') as f:
                f.write(band_img)
            click.echo(f"Band image saved as {_filename}")

if __name__ == '__main__':
    main()
