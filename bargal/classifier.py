from typing import Union

import numpy as np
from torch import nn
from torchvision import transforms
from PIL import Image
from io import BytesIO

from bargal.images.client import GalaxyImageClient
from bargal.models import GalaxyDict, Galaxy
from bargal.preprocessing import ImageProcessor


class GalaxyClassifier:

    def __init__(self, img_preprocessor: ImageProcessor, img_client: GalaxyImageClient, state_dict: dict):
        self.img_preprocessor = img_preprocessor
        self.img_client = img_client

        self.model = nn.Sequential(
            # First conv layer
            nn.Conv2d(1, 8, kernel_size=3, stride=1, padding=1),  # 8 x 400 x 400
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2),  # 8 x 200 x 200

            ## Flattening
            nn.Flatten(),
            nn.Linear(8 * 200 * 200, 512),
            nn.Dropout(.3),
            nn.ReLU(),
            nn.Linear(512, 1)
        )

        self.model.load_state_dict(state_dict)
        self.model.eval()

    def classify(self, galaxy: Union[Galaxy, GalaxyDict]) -> bool:
        observation = self.img_client.get_as_observation(galaxy, use_fits=True, skip_rgb=True)
        processed = self.img_preprocessor.preprocess(observation)
        processed = (processed * 255).astype(np.uint8)

        img = Image.fromarray(processed, mode='L')

        return self._predict(img)

    def _predict(self, processed_img: np.ndarray) -> bool:
        tensor = transforms.ToTensor()(processed_img).unsqueeze(0)
        model_output = self.model(tensor)
        return model_output.item() > 0