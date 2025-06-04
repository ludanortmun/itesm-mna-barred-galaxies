from abc import ABC, abstractmethod

import numpy as np

from bargal.images.transformations import (
    sqrt_transformer,
    adaptive_normalize_transformer,
    bilateral_filter_transformer,
    make_image_pipeline,
    ImageTransformer,
    log_transformer,
    center_zoom_transformer,
    circular_mask_transformer,
    normalize_transformer,
    remove_background_transformer,
    squared_transformer,
    power_transformer,
)
from bargal.models import Observation


class ImageProcessor(ABC):
    """
    Base class for image processors. An ImageProcessor is responsible for transforming
    an Observation into a single image represented as a numpy array.
    The dimensionality of the output image is determined by each specific implementation.
    """

    @abstractmethod
    def preprocess(self, obs: Observation) -> np.ndarray:
        """
        Abstract method to preprocess an observation.
        Must be implemented by subclasses.
        """
        pass


class RGBProcessor(ImageProcessor):
    """
    RGBProcessor is an implementation of ImageProcessor that only transforms the RGB representation of the observation.
    """

    def __init__(self, transform: ImageTransformer):
        """
        Initialize a new RBGProcessor.

        Args:
            transform (ImageTransformer): A transformation to be applied to the RGB representation of the observation.
        """
        self.transform = transform

    def preprocess(self, obs: Observation) -> np.ndarray:
        r = self.transform(obs.rgb_repr[:,:,0])
        g = self.transform(obs.rgb_repr[:,:,1])
        b = self.transform(obs.rgb_repr[:,:,2])

        return np.stack([r,g,b], axis=-1)


class GRRatioProcessor(ImageProcessor):
    def __init__(self, *,
                 g_transform: ImageTransformer,
                 r_transform: ImageTransformer,
                 result_transform: ImageTransformer) -> None:
        """
        Initialize the GRRatioProcessor with specific image processing pipelines for g and r bands.

        Args:
            g_transform (ImageTransformer): Transformation for the g band.
            r_transform (ImageTransformer): Transformation for the r band.
            result_transform (ImageTransformer): Transformation for the result after computing the division.
        """
        self.g_transform = g_transform
        self.r_transform = r_transform
        self.result_transform = result_transform

    def preprocess(self, obs: Observation) -> np.ndarray:
        """
        Implementation of the preprocess method for GRRatioProcessor.
        """
        return self.result_transform(
            self.g_transform(obs.g_band) / (self.r_transform(obs.r_band) + np.finfo(float).eps)
        )

class GRDiffProcessor(ImageProcessor):
    """
    GRDiffProcessor is a specialized image processor that computes the difference between
    two images (g and r bands). It applies different transformations to each band before computing the difference.
    The result is then processed with a final transformation pipeline.
    This implementation will always return a 1-channel image.
    """

    def __init__(self, *,
                 g_transform: ImageTransformer,
                 r_transform: ImageTransformer,
                 result_transform: ImageTransformer) -> None:
        """
        Initialize the GRDiffProcessor with specific image processing pipelines for g and r bands.

        Args:
            g_transform (ImageTransformer): Transformation for the g band.
            r_transform (ImageTransformer): Transformation for the r band.
            result_transform (ImageTransformer): Transformation for the result after computing the difference.
        """
        self.g_transform = g_transform
        self.r_transform = r_transform
        self.result_transform = result_transform

    def preprocess(self, obs: Observation) -> np.ndarray:
        """
        Implementation of the preprocess method for GRDiffProcessor.
        """
        return self.result_transform(
            self.g_transform(obs.g_band) - self.r_transform(obs.r_band)
        )


SQRT_GR_DIFF = GRDiffProcessor(
    g_transform=make_image_pipeline(
        adaptive_normalize_transformer(),
        bilateral_filter_transformer()
    ),
    r_transform=make_image_pipeline(
        adaptive_normalize_transformer(),
    ),
    result_transform=make_image_pipeline(
        sqrt_transformer(),
        adaptive_normalize_transformer(),
        center_zoom_transformer(1.25),
    )
)

GRLOG_GR_DIFF = GRDiffProcessor(
    g_transform=make_image_pipeline(
        adaptive_normalize_transformer(),
        bilateral_filter_transformer()
    ),
    r_transform=make_image_pipeline(
        log_transformer()
    ),
    result_transform=make_image_pipeline(
        center_zoom_transformer(1.25),
        adaptive_normalize_transformer(),
    )
)

GRLOG_GR_DIFF_MASKED = GRDiffProcessor(
    g_transform=make_image_pipeline(
        adaptive_normalize_transformer(),
        bilateral_filter_transformer()
    ),
    r_transform=make_image_pipeline(
        log_transformer()
    ),
    result_transform=make_image_pipeline(
        center_zoom_transformer(1.25),
        adaptive_normalize_transformer(),
        circular_mask_transformer()
    )
)

CROP_RGB=RGBProcessor(
    transform=make_image_pipeline(
        center_zoom_transformer(1.25),
        normalize_transformer(),
    )
)

GR_RATIO = GRRatioProcessor(
    g_transform=make_image_pipeline(
        remove_background_transformer(),
        adaptive_normalize_transformer(),
        bilateral_filter_transformer()
    ),
    r_transform=make_image_pipeline(
        squared_transformer(),
        normalize_transformer()
    ),
    result_transform=make_image_pipeline(
        center_zoom_transformer(1.25),
        adaptive_normalize_transformer(),
        power_transformer(2.5),
    )
)

GR_SQUARED_DIFF = GRDiffProcessor(
    g_transform=squared_transformer(),
    r_transform=squared_transformer(),
    result_transform=make_image_pipeline(
        center_zoom_transformer(1.25),
        adaptive_normalize_transformer()
    ),
)


PREPROCESSORS = {
    'SQRT_GR_DIFF': SQRT_GR_DIFF,
    'GRLOG_GR_DIFF': GRLOG_GR_DIFF,
    'GRLOG_GR_DIFF_MASKED': GRLOG_GR_DIFF_MASKED,
    'CROP_RGB': CROP_RGB,
    'GR_RATIO': GR_RATIO,
    'GR_SQUARED_DIFF': GR_SQUARED_DIFF,
}
