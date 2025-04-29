from typing import Union

import requests

from bargal.images.storage import ImageFileStore
from bargal.models import Galaxy, GalaxyDict

url_template = "https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&size=800&layer=ls-dr10&pixscale=0.262&bands=grz"


class GalaxyImageClient:
    def __init__(self, *, local_dir=None) -> None:
        self._memcache = {}
        self._diskcache = None
        if local_dir is not None:
            self._diskcache = ImageFileStore(local_dir)

    def get_image(self, galaxy: Union[Galaxy, GalaxyDict]):
        """
        Fetches the image for a given galaxy.

        Args:
            galaxy (Galaxy): The galaxy object containing its name, RA and DEC.

        Returns:
            bytes: The image data.
        """
        g = galaxy if isinstance(galaxy, Galaxy) else Galaxy.from_dict(galaxy)

        if g.name in self._memcache:
            return self._memcache[g.name]
        elif self._diskcache and self._diskcache.has_image(f"{g.name}.jpg"):
            return self._diskcache.load_image(f"{g.name}.jpg")

        image = self._download_image(g)
        self._memcache[g.name] = image

        if self._diskcache:
            self._diskcache.save_image(f"{g.name}.jpg", image)

        return image

    def _download_image(self, galaxy: Galaxy) -> bytes:
        print(f"Downloading image for {galaxy.name} at RA: {galaxy.ra}, DEC: {galaxy.dec}")

        url = url_template.format(ra=galaxy.ra, dec=galaxy.dec)

        response = requests.get(url)
        response.raise_for_status()

        return response.content
