import enum
from dataclasses import dataclass
from typing import TypedDict, Optional

import numpy as np


@dataclass
class Observation:
    """
    Dataclass representing an observation of a galaxy.

    Attributes:
        rgb_repr (np.ndarray): The RGB representation of the galaxy image.
        g_band (np.ndarray): The G band data.
        r_band (np.ndarray): The R band data.
        z_band (np.ndarray): The Z band data.
    """
    rgb_repr: np.ndarray
    g_band: np.ndarray
    r_band: np.ndarray
    z_band: np.ndarray


class GalaxyBar(enum.Enum):
    UNKNOWN = -0.5  # no determinado
    NO_BAR = 0.0  # no barra
    WEAK_BAR = 0.25  # barra débil
    MIXED_BAR = 0.5  # barra mezclada con los brazos
    DEFINED_BAR = 0.75  # barra definida en el centro
    STRONG_BAR = 1.0  # barra definida que es de un tamaño importante


class GalaxyDict(TypedDict):
    """
    TypedDict for Galaxy data. This matches the structure of the dataset.
    """

    name: str
    objra: float
    objdec: float
    Bars: float


class Galaxy:
    """
    Class representing a galaxy with its properties. Used for programatic operations.
    """

    def __init__(self, name: str, ra: float, dec: float):
        self.name = name
        self.ra = ra
        self.dec = dec
        self.bar = GalaxyBar.UNKNOWN
        self.image: Optional[bytes] = None

    @classmethod
    def from_dict(cls, data: GalaxyDict) -> 'Galaxy':
        galaxy = cls(data['name'], data['objra'], data['objdec'])
        if 'Bars' in data:
            galaxy.bar = GalaxyBar(data['Bars'])
        return galaxy

    def to_dict(self) -> GalaxyDict:
        return {'name': self.name, 'objra': self.ra, 'objdec': self.dec, 'Bars': self.bar.value}
