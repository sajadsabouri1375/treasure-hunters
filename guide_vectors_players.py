from players import Player
import numpy as np
from vector_utils import VectorUtils


class GuideVectorsPlayer(Player):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._number_of_feasible_moving_vectors = kwargs.get('number_of_vectors', 8)
        self._angle_spacing = 2 * np.pi / self._number_of_feasible_moving_vectors
        self._feasible_move_vectors = []
    
    def get_feasible_move_vectors(self):
        return self._feasible_move_vectors
    
    def build_feasible_move_vectors(self):
        
        if (self._previous_move_vector == np.zeros((1,2))).all():
            base_vector = np.array([1,0]).reshape(1, -1)
        else:
            base_vector = VectorUtils.find_unit_vector(self._previous_move_vector)
        
        base_vector_angle = VectorUtils.find_vector_angle(base_vector)
        
        self._feasible_move_vectors = [
            VectorUtils.find_angle_vector(base_vector_angle + i * self._angle_spacing)
            for i in range(self._number_of_feasible_moving_vectors)
        ]