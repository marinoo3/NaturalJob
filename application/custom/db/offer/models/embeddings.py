import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass

Vector50 = NDArray[np.float32]  # or np.float32, etc.
Vector3 = NDArray[np.float32]

@dataclass
class Embeddings:
    d50: Vector50
    d3: Vector3