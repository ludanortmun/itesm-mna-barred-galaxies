from typing import Union

import requests

from bargal.images.storage import ImageFileStore
from bargal.models import Galaxy, GalaxyDict

url_template = "https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&size=800&layer=ls-dr10&pixscale=0.262&bands=grz"


def _download_image(galaxy: Galaxy) -> bytes:
    print(f"Downloading image for {galaxy.name} at RA: {galaxy.ra}, DEC: {galaxy.dec}")

    url = url_template.format(ra=galaxy.ra, dec=galaxy.dec)

    response = requests.get(url)
    response.raise_for_status()

    return response.content


class GalaxyImageClient:
    def __init__(self, *, storage_path=None) -> None:
        self._memcache = {}
        self._diskcache = None
        self.storage_path = storage_path
        if storage_path is not None:
            self._diskcache = ImageFileStore(storage_path)

    def get_image(self, galaxy: Union[Galaxy, GalaxyDict], *, save_to_disk: bool = True) -> bytes:
        """
        Gets a galaxy image from disk cache, memory cache, or downloads it.

        Args:
            galaxy (Galaxy): The galaxy object containing its name, RA and DEC.
            save_to_disk (bool): If True and storage_path is set, saves downloaded image to disk.
                                Ignored if storage_path was not provided. Default: True.

        Returns:
            bytes: The image data.

        Side Effects:
            - Always caches downloaded images in memory
            - If storage_path was set and save_to_disk=True, saves downloaded images to disk
        """
        g = galaxy if isinstance(galaxy, Galaxy) else Galaxy.from_dict(galaxy)

        # Try memory cache first
        if g.name in self._memcache:
            return self._memcache[g.name]

        # Try disk cache if available
        if self._diskcache and self._diskcache.has_image(f"{g.name}.jpg"):
            image = self._diskcache.load_image(f"{g.name}.jpg")
            self._memcache[g.name] = image  # Cache in memory for future use
            return image

        # Download if not found in cache
        image = _download_image(g)
        self._memcache[g.name] = image

        # Save to disk if enabled
        if self._diskcache and save_to_disk:
            self._diskcache.save_image(f"{g.name}.jpg", image)

        return image
