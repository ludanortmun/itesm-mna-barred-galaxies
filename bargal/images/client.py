from typing import Union

import requests

from bargal.images.storage import ImageFileStore
from bargal.models import Galaxy, GalaxyDict

url_template = "https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&size=800&layer=ls-dr10&pixscale=0.262&bands={bands}"
supported_bands = {'g', 'r', 'z'}

def _download_image(galaxy: Galaxy, *, bands: str = 'grz') -> bytes:
    print(f"Downloading image for {galaxy.name} at RA: {galaxy.ra}, DEC: {galaxy.dec}; bands: {bands}")

    url = url_template.format(ra=galaxy.ra, dec=galaxy.dec, bands=bands)

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

    def _get_cached(self, name: str) -> bytes or None:
        # Try memory cache first
        if name in self._memcache:
            return self._memcache[name]

        # Try disk cache if available
        if self._diskcache and self._diskcache.has_image(f"{name}.jpg"):
            image = self._diskcache.load_image(f"{name}.jpg")
            self._memcache[name] = image  # Cache in memory for future use
            return image

        return None

    def get_image(self, galaxy: Union[Galaxy, GalaxyDict], *, save_to_disk: bool = True) -> bytes:
        """
        Gets a galaxy image from disk cache, memory cache, or downloads it.
        The image itself will be an RGB representation of the G, R, and Z bands.

        Args:
            galaxy (Galaxy): The galaxy object containing its name, RA, and DEC.
            save_to_disk (bool): If True and if storage_path is set, saves downloaded image to disk.
                                Ignored if storage_path was not provided. Default: True.

        Returns:
            bytes: The image data.

        Side Effects:
            - Always caches downloaded images in memory
            - If storage_path was set and save_to_disk=True, saves downloaded images to disk
        """
        g = galaxy if isinstance(galaxy, Galaxy) else Galaxy.from_dict(galaxy)

        cached = self._get_cached(g.name)
        if cached:
            return cached

        # Download if not found in the cache
        image = _download_image(g)
        self._memcache[g.name] = image

        # Save to disk if enabled
        if self._diskcache and save_to_disk:
            self._diskcache.save_image(f"{g.name}.jpg", image)

        return image

    def get_image_as_bands(self,
                           galaxy: Union[Galaxy, GalaxyDict],
                           *,
                           save_to_disk: bool = True,
                           bands='grz') -> dict[str, bytes]:
        """
        Gets a galaxy image with specific bands from disk cache, memory cache, or downloads it.

        Args:
            galaxy (Galaxy): The galaxy object containing its name, RA, and DEC.
            save_to_disk (bool): If True and if storage_path is set, saves downloaded image to disk.
                                Ignored if storage_path was not provided. Default: True.
            bands (str): The bands to use for the image. Default: 'grz'.

        Returns:
            dict[str, bytes]: A dictionary containing the image data for each band.
            Each key of the dictionary will correspond to a band, and the value will be the image data for that band.
        """
        g = galaxy if isinstance(galaxy, Galaxy) else Galaxy.from_dict(galaxy)
        result = {}

        for band in set(bands).intersection(supported_bands):
            img_name = f"{g.name}.{band}"
            cached = self._get_cached(img_name)
            if cached:
                result[band] = cached
                continue

            # Download if not found in the cache
            image = _download_image(g, bands=band)
            self._memcache[img_name] = image
            result[band] = image

            # Save to disk if enabled
            if self._diskcache and save_to_disk:
                self._diskcache.save_image(f"{img_name}.jpg", image)

        return result
