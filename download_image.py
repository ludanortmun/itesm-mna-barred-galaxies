import click
import requests

url_template = "https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&size=800&layer=ls-dr10&pixscale=0.262&bands=grz"

def download_image(ra: float, dec: float, name: str = None) -> None:
    url = url_template.format(ra=ra, dec=dec)
    filename = f"{name or f'cutout_ra{ra}_dec{dec}'}.jpg"

    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            f.write(response.content)
        click.echo(f"Image saved as {filename}")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error downloading image: {e}", err=True)

@click.command()
@click.argument('ra', type=float)
@click.argument('dec', type=float)
@click.option('--name', '-n', help='Custom filename (without extension)')
def main(ra: float, dec: float, name: str) -> None:
    """Download JPEG cutout from Legacy Survey using coordinates."""
    download_image(ra, dec, name)

if __name__ == '__main__':
    main()