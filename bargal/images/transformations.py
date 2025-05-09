from typing import Callable

import numpy as np
from astropy.visualization import PowerStretch, LogStretch, AsinhStretch, SqrtStretch, SquaredStretch


def power_transform(exponent: float) -> Callable[[np.ndarray], np.ndarray]:
    """
    Apply power transformation to the image.

    Args:
        exponent (float): The exponent for the power transformation.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that applies the power transformation to an image.
    """
    return PowerStretch(exponent)
    # return lambda image: np.clip(image ** exponent, 0, 1)


def log_transform() -> Callable[[np.ndarray], np.ndarray]:
    """
    Apply logarithmic transformation to the image.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that applies the logarithmic transformation to an image.
    """
    return LogStretch()
    # return lambda image: np.clip(np.log(1 + image), 0, 1)


def asinh_transform() -> Callable[[np.ndarray], np.ndarray]:
    """
    Apply inverse hyperbolic sine transformation to the image.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that applies the inverse hyperbolic sine transformation to the image.
    """
    return AsinhStretch()
    # return lambda image: np.clip(np.arcsinh(image), 0, 1)


def squared_transform() -> Callable[[np.ndarray], np.ndarray]:
    """
    Apply squared transformation to the image.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that applies the squared transformation to the image.
    """
    return SquaredStretch()


def sqrt_transform() -> Callable[[np.ndarray], np.ndarray]:
    """
    Apply square root transformation to the image.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that applies the square root transformation to the image.
    """
    return SqrtStretch()

