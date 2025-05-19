from io import BytesIO
from typing import Union, Optional

import numpy as np
import requests
from PIL import Image
from astropy.io import fits

from bargal.images.storage import ImageFileStore
from bargal.models import Galaxy, GalaxyDict, Observation

url_template = ("https://www.legacysurvey.org/viewer/{img_format}-cutout"
                "?ra={ra}&dec={dec}&size=800&layer=ls-dr10&pixscale=0.262&bands={bands}")
supported_bands = {'g', 'r', 'z'}


def _download_image(galaxy: Galaxy, *, bands: str = 'grz', img_format="jpeg") -> bytes:
    if img_format.lower() not in ['jpeg', 'fits']:
        raise ValueError(f"Unsupported image format: {img_format}. Supported formats are 'jpeg' and 'fits'.")

    print(f"Downloading {img_format} image for {galaxy.name} at RA: {galaxy.ra}, DEC: {galaxy.dec}; bands: {bands}")

    url = url_template.format(img_format=img_format, ra=galaxy.ra, dec=galaxy.dec, bands=bands)

    response = requests.get(url)
    response.raise_for_status()

    return response.content


def _bytes_to_image_array(img_data: bytes, *, grayscale: bool) -> np.ndarray:
    """
    Converts bytes to an array representing the image. If grayscale is True, converts to grayscale.

    Args:
        img_data (bytes): The image data in bytes.
        grayscale (bool): If True, converts the image to grayscale.
    """

    img = Image.open(BytesIO(img_data))
    if grayscale:
        img = img.convert('L')

    return np.array(img)


class GalaxyImageClient:
    def __init__(self, *, storage_path=None) -> None:
        self._diskcache = None
        self.storage_path = storage_path
        if storage_path is not None:
            self._diskcache = ImageFileStore(storage_path)

    def _get_cached(self, name: str) -> Optional[bytes]:
        # Try disk cache if available
        if self._diskcache and self._diskcache.has_image(name):
            image = self._diskcache.load_image(name)
            return image

        return None

    def get_image(self, galaxy: Union[Galaxy, GalaxyDict], *, save_to_disk: bool = True) -> bytes:
        """
        Gets a galaxy image from a disk cache or downloads it.
        The image itself will be an RGB representation of the G, R, and Z bands.

        Args:
            galaxy (Galaxy): The galaxy object containing its name, RA, and DEC.
            save_to_disk (bool): If True and if storage_path is set, saves downloaded image to disk.
                                Ignored if storage_path was not provided. Default: True.

        Returns:
            bytes: The image data.

        Side Effects:
            - If storage_path was set and save_to_disk=True, saves downloaded images to disk
        """
        g = galaxy if isinstance(galaxy, Galaxy) else Galaxy.from_dict(galaxy)

        cached = self._get_cached(f"{g.name.strip()}.jpg")
        if cached:
            return cached

        # Download if not found in the cache
        image = _download_image(g)

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
            img_name = f"{g.name.strip()}.{band}.jpg"
            cached = self._get_cached(img_name)
            if cached:
                result[band] = cached
                continue

            # Download if not found in the cache
            image = _download_image(g, bands=band)
            result[band] = image

            # Save to disk if enabled
            if self._diskcache and save_to_disk:
                self._diskcache.save_image(img_name, image)

        return result

    def get_as_observation(self,
                           galaxy: Union[Galaxy, GalaxyDict],
                           *,
                           save_to_disk: bool = True,
                           use_fits: bool = False,
                           skip_rgb: bool = False) -> Observation:
        """
        Gets an Observation object for a galaxy.
        Images are retrieved from disk cache, memory cache, or downloaded.

        Args:
            galaxy (Galaxy): The galaxy object containing its name, RA, and DEC.
            save_to_disk (bool): If True and if storage_path is set, saves downloaded image to disk.
                                Ignored if storage_path was not provided. Default: True.
            use_fits (bool): If True, retrieves the FITS image for individual bands. Default: False.
            skip_rgb (bool): If True, skips the RGB image retrieval. Default: False.

        Returns:
            Observation: An Observation object containing the RGB representation and individual band data.
        """
        g = galaxy if isinstance(galaxy, Galaxy) else Galaxy.from_dict(galaxy)

        rgb = None
        if not skip_rgb:
            # Get the RGB image using the existing method
            rgb = self.get_image(g, save_to_disk=save_to_disk)

        # If not using FITS for individual bands, retrieve the bands as JPEG images using the existing method
        if not use_fits:
            bands = self.get_image_as_bands(g, save_to_disk=save_to_disk, bands='grz')
            return Observation(rgb_repr=_bytes_to_image_array(rgb, grayscale=False),
                               g_band=_bytes_to_image_array(bands['g'], grayscale=True),
                               r_band=_bytes_to_image_array(bands['r'], grayscale=True),
                               z_band=_bytes_to_image_array(bands['z'], grayscale=True))

        # Otherwise, we download the FITS image for the galaxy.
        # A benefit of this is that a single download will contain all three bands as separate channels.
        fits_img_name = f"{g.name.strip()}.fits"
        fits_data = self._get_cached(fits_img_name)
        if not fits_data:
            fits_data = _download_image(g, bands='grz', img_format='fits')

            # Save to disk if enabled
            if self._diskcache and save_to_disk:
                self._diskcache.save_image(fits_img_name, fits_data)

        g, r, z = None, None, None
        with fits.open(BytesIO(fits_data)) as fits_img:
            g = fits_img[0].data[0]
            r = fits_img[0].data[1]
            z = fits_img[0].data[2]

        return Observation(rgb_repr=_bytes_to_image_array(rgb, grayscale=False) if rgb else None,
                           g_band=np.flip(g, axis=0),
                           r_band=np.flip(r, axis=0),
                           z_band=np.flip(z, axis=0))
