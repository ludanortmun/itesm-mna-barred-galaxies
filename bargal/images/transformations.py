from typing import Callable

import cv2
import numpy as np
from astropy.visualization import PowerStretch, LogStretch, AsinhStretch, SquaredStretch


class ImageTransformer:
    """
    A wrapper class for image transformation functions.

    This class encapsulates a transformation function that operates on an image
    (a NumPy array) and provides a callable interface for applying the transformation.

    Attributes:
        transform (Callable[[np.ndarray], np.ndarray]): The transformation function to be applied.

    Methods:
        __call__(image: np.ndarray) -> np.ndarray:
            Apply the transformation to the given image.
        apply(image: np.ndarray) -> np.ndarray:
            Apply the transformation to the given image (alternative to __call__).
    """
    def __init__(self, transform: Callable[[np.ndarray], np.ndarray]):
        self.transform = transform

    def __call__(self, image: np.ndarray) -> np.ndarray:
        """
        Apply the transformation to the given image.

        Args:
            image (np.ndarray): The input image to transform.

        Returns:
            np.ndarray: The transformed image.
        """
        return self.transform(image)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        Apply the transformation to the given image.

        Args:
            image (np.ndarray): The input image to transform.

        Returns:
            np.ndarray: The transformed image.
        """
        return self.transform(image)


def make_image_pipeline(*transformers: ImageTransformer) -> ImageTransformer:
    """
    Create a pipeline of image transformations.

    Args:
        *transformers (ImageTransformer): A variable number of ImageTransformer instances.

    Returns:
        ImageTransformer: A new ImageTransformer that applies the transformations in sequence.
    """
    def pipeline(image: np.ndarray) -> np.ndarray:
        for transformer in transformers:
            image = transformer(image)
        return image

    return ImageTransformer(pipeline)

# Below are our pre-defined transformer functions. They are, for the most part, simple functions that just
# call a function from a variety of libraries, like OpenCV or Astropy. While we could call them directly
# in client code, we wrap them in the ImageTransformer class to provide a consistent interface.
# Additionally, this approach makes it easier to swap implementations in the future if needed.
# Note that for now, we only have simple 1-band transformers.


def power_transformer(exponent: float) -> ImageTransformer:
    """
    Apply power transformation to the image.

    Args:
        exponent (float): The exponent for the power transformation.

    Returns:
        ImageTransformer: An ImageTransformer that applies the power transformation to an image.
    """
    return ImageTransformer(PowerStretch(exponent))
    # return lambda image: np.clip(image ** exponent, 0, 1)


def log_transformer() -> ImageTransformer:
    """
    Apply logarithmic transformation to the image.

    Returns:
        ImageTransformer: An ImageTransformer that applies the logarithmic transformation to an image.
    """
    return ImageTransformer(LogStretch())


def asinh_transformer() -> ImageTransformer:
    """
    Apply inverse hyperbolic sine transformation to the image.

    Returns:
        ImageTransformer: An ImageTransformer that applies the inverse hyperbolic sine transformation to the image.
    """
    return ImageTransformer(AsinhStretch())


def squared_transformer() -> ImageTransformer:
    """
    Apply squared transformation to the image.

    Returns:
        ImageTransformer: An ImageTransformer that applies the squared transformation to the image.
    """
    return ImageTransformer(SquaredStretch())


def sqrt_transformer() -> ImageTransformer:
    """
    Apply square root transformation to the image.

    Returns:
        ImageTransformer: An ImageTransformer that applies the square root transformation to the image.
    """

    def _sqrt(image: np.ndarray) -> np.ndarray:
        # Ensures the image is non-negative and handles NaN and Inf values
        image_safe = np.maximum(np.nan_to_num(image, nan=0.0, posinf=0.0, neginf=0.0), 0)
        return np.sqrt(image_safe)

    return ImageTransformer(_sqrt)


def threshold_transformer(threshold_value: int = 127) -> ImageTransformer:
    """
    Apply global threshold transformation to the image.

    Args:
        threshold_value (int): The threshold value. Default is 127.

    Returns:
        ImageTransformer: An ImageTransformer that applies the threshold transformation to an image.
    """
    def apply_threshold(image: np.ndarray) -> np.ndarray:
        _, binary_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        return binary_image

    return ImageTransformer(apply_threshold)


def adaptive_threshold_transformer(*,
                                   block_size: int = 11, C: int = 2
                                   ) -> ImageTransformer:
    """
    Apply adaptive threshold transformation to the image.

    Args:
        block_size (int): Size of the pixel neighborhood that is used to calculate a threshold value for the pixel. Default is 11.
        C (int): Constant subtracted from the mean or weighted mean. Default is 2.

    Returns:
        ImageTransformer: An ImageTransformer that applies the adaptive threshold transformation to an image.
    """
    def apply_adaptive_threshold(image: np.ndarray) -> np.ndarray:
        image_uint8 = (image * 255).astype(np.uint8) if image.max() <= 1.0 else image
        return cv2.adaptiveThreshold(
            image_uint8, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C
        )

    return ImageTransformer(apply_adaptive_threshold)


def gaussian_blur_transformer(kernel_size: int = 5) -> ImageTransformer:
    """
    Apply Gaussian blur to the image.

    Args:
        kernel_size (int): Size of the Gaussian kernel. Default is 5.

    Returns:
        ImageTransformer: An ImageTransformer that applies Gaussian blur to an image.
    """
    return ImageTransformer(lambda image: cv2.GaussianBlur(image, (kernel_size, kernel_size), 0))


def median_blur_transformer(kernel_size: int = 5) -> ImageTransformer:
    """
    Apply median blur to the image.

    Args:
        kernel_size (int): Size of the kernel. Default is 5.

    Returns:
        ImageTransformer: An ImageTransformer that applies median blur to an image.
    """
    return ImageTransformer(lambda image: cv2.medianBlur(image, kernel_size))


def bilateral_filter_transformer(
        *,
        diameter: int = 9,
        sigma_color: float = 75,
        sigma_space: float = 75) -> ImageTransformer:
    """
    Apply bilateral filter to the image.

    Args:
        diameter (int): Diameter of the pixel neighborhood. Default is 9.
        sigma_color (float): Filter sigma in color space. Default is 75.
        sigma_space (float): Filter sigma in coordinate space. Default is 75.

    Returns:
        ImageTransformer: An ImageTransformer that applies bilateral filter to an image.
    """
    return ImageTransformer(lambda image: cv2.bilateralFilter(image, diameter, sigma_color, sigma_space))


def normalize_transformer() -> ImageTransformer:
    """
    Normalize the image to the range [0, 1].

    Returns:
        ImageTransformer: An ImageTransformer that normalizes an image.
    """
    def _normalize(image: np.ndarray) -> np.ndarray:
        image = (image - np.min(image)) / (np.max(image) - np.min(image))
        return image.astype(np.float32)

    return ImageTransformer(_normalize)


def adaptive_normalize_transformer() -> ImageTransformer:
    """
    Normalize the image to the range [0, 1] using an adaptive approach intended for FITS images.
    This will take the 1 and 99 percentiles of the input image and use them to normalize the image.

    Returns:
        ImageTransformer: An ImageTransformer that applies adaptive normalization to an image.
    """

    def _normalize_adaptive(image: np.ndarray) -> np.ndarray:
        p_low, p_high = np.percentile(image, (1, 99))  # Rango adaptativo
        image_normalized = np.clip((image - p_low) / (p_high - p_low), 0, 1)
        return image_normalized.astype(np.float32)

    return ImageTransformer(_normalize_adaptive)
