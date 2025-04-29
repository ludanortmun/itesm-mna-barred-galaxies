import click
from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy


@click.command()
@click.argument('ra', type=float)
@click.argument('dec', type=float)
@click.option('--name', '-n', help='Custom filename (without extension)')
def main(ra: float, dec: float, name: str) -> None:
    """Download JPEG cutout from Legacy Survey using coordinates."""
    g = Galaxy(name, ra, dec)
    client = GalaxyImageClient()
    img_data = client.get_image(g)


    filename = f"{g.name or f'cutout_ra{ra}_dec{dec}'}.jpg"
    with open(filename, 'wb') as f:
        f.write(img_data)
    click.echo(f"Image saved as {filename}")

if __name__ == '__main__':
    main()