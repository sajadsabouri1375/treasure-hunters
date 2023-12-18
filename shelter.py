import numpy as np


class Shelter:
    def __init__(self, **kwargs):
        self._position = kwargs.get('position', np.zeros((1, 2)))

    def get_position(self):
        return self._position