import typing
from abc import ABC, abstractmethod
from typing import Union

from bargal.images.client import GalaxyImageClient
from bargal.models import Galaxy, GalaxyDict, Observation


class BasePredictor(ABC):
    """
    Base class for all predictors.
    """

    def __init__(self, img_client: GalaxyImageClient) -> None:
        self._img_client = img_client

    def classify(self, galaxy: Union[Galaxy, GalaxyDict]) -> bool:
        """
        Classifies a galaxy as barred or not.

        :param galaxy: The information of the galaxy to classify.
        It should contain at least the name and RA and DEC coordinates.
        :return: True if the galaxy is barred, False otherwise.
        """

        observation = self._img_client.get_as_observation(galaxy, use_fits=True, skip_rgb=True)
        processed = self._prepare_features(observation)
        return self._predict(processed)

    @abstractmethod
    def _prepare_features(self, obs: Observation) -> typing.Any:
        """
        Abstract method to transform the raw galaxy Observation into the features used by the predictor model.
        Each predictor must implement this method.

        :param obs: A raw galaxy Observation.
        :return: The features used by the predictor model. The type of the features can vary
        based on the concrete implementation.
        """
        pass

    @abstractmethod
    def _predict(self, features: typing.Any) -> bool:
        """
        Abstract method that returns a prediction based on the given features.
        Each predictor must implement this method.

        :param features: The preprocessed features used for prediction. These features are derived from a galaxy
        Observation and processed using the _prepare_features method.
        :return: A boolean indicating whether the provided Galaxy is barred or not.
        """
        pass
