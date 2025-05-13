import numpy as np

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


class GRDiffProcessor:
    def __init__(self, *,
                 g_transform: ImageTransformer,
                 r_transform: ImageTransformer,
                 result_transform: ImageTransformer) -> None:
        """
        Initialize the GRDiffProcessor with specific image processing pipelines for g and r bands.
        """
        self.g_pipeline = g_transform
        self.r_pipeline = r_transform
        self.result_pipeline = result_transform

    def preprocess(self, obs: Observation) -> np.ndarray:
        """
        Preprocess the observation by calculating the difference between the g and r bands.

        Args:
            obs (Observation): The observation object containing the image data.

        Returns:
            np.ndarray: The preprocessed image data.
        """

        return self.result_pipeline(
            self.g_pipeline(obs.g_band) - self.r_pipeline(obs.r_band)
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
