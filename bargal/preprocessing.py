import numpy as np
from abc import ABC, abstractmethod

from bargal.images.transformations import (
    sqrt_transformer,
    adaptive_normalize_transformer,
    bilateral_filter_transformer,
    make_image_pipeline,
    normalize_transformer,
    ImageTransformer,
    log_transformer,
    center_crop
)
from bargal.models import Observation


class ImageProcessor(ABC):
    @abstractmethod
    def preprocess(self, obs: Observation) -> np.ndarray:
        """
        Abstract method to preprocess an observation.
        Must be implemented by subclasses.
        """
        pass


class GRDiffProcessor(ImageProcessor):
    """
    GRDiffProcessor is a specialized image processor that computes the difference between
    two images (g and r bands). It applies different transformations to each band before computing the difference.
    The result is then processed with a final transformation pipeline.
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
        center_crop(),
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
        center_crop(),
        adaptive_normalize_transformer(),
    )
)

PREPROCESSORS = {
    'SQRT_GR_DIFF': SQRT_GR_DIFF,
    'GRLOG_GR_DIFF': GRLOG_GR_DIFF
}

