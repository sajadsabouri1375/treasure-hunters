import numpy as np


class Treasure:
    def __init__(self, **kwargs):
        self._current_position = kwargs.get('current_position', np.zeros((1, 2)))
        self._is_hunted = kwargs.get('is_hunted', False)
        
    def get_current_position(self):
        return self._current_position