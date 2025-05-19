import os
import typing

import cv2
import joblib
import numpy as np
import pandas as pd

from bargal.images.client import GalaxyImageClient
from bargal.models import Observation
from bargal.predictors.base import BasePredictor
from bargal.preprocessing import GRLOG_GR_DIFF


class MLPBaselinePredictor(BasePredictor):
    """
    Baseline predictor model using an MLP to detect bars in galaxies.
    """
    def __init__(self, img_client: GalaxyImageClient):
        super().__init__(img_client)
        self.img_processor = GRLOG_GR_DIFF

        this_dir, this_filename = os.path.split(__file__)
        model_path = os.path.join(this_dir, "mlp.pkl")
        scaler_path = os.path.join(this_dir, "scaler.pkl")

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)


    def _predict(self, features: np.ndarray) -> bool:
        features_scaled = self.scaler.transform(features)
        return bool(self.model.predict(features_scaled))

    def _prepare_features(self, obs: Observation) -> typing.Any:
        # This implementation applies the GRLOG_GR_DIFF transform to the raw observation
        # to get a grayscale image for the galaxy.
        # It then extracts scalar attributes from the resulting image and uses them as features for the model.
        processed = self.img_processor.preprocess(obs)
        processed = (processed * 255).astype(np.uint8)
        return pd.DataFrame([self._image_to_features(processed)],
                            columns=["contrast", "edge_count", "hist_std", "circularity"])

    @classmethod
    def _image_to_features(cls, img: np.ndarray):
        image = img

        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_std = np.std(hist)

        edges = cv2.Canny(image, 100, 200)
        edge_count = np.sum(edges > 0)

        glcm = cv2.calcHist([image], [0], None, [256], [0, 256])
        contrast = np.var(glcm)

        _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            perimeter = cv2.arcLength(largest_contour, True)
            area_contour = cv2.contourArea(largest_contour)
            circularity = 4 * np.pi * (area_contour / (perimeter ** 2)) if perimeter > 0 else 0
        else:
            circularity = 0

        return np.array([
            contrast,
            edge_count,
            hist_std,
            circularity
        ])