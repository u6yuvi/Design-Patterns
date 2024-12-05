from typing import List, Tuple, Union

import numpy as np


def manhattan_distance(a: Union[Tuple, List], b: Union[Tuple, List]) -> float:
    """
    Calculate manhattan distance between two points
    """
    a = np.array(a)
    b = np.array(b)
    m_dist = np.sum(np.abs(a - b))
    return m_dist
