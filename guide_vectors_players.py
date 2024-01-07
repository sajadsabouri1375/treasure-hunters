'''
    This class extends BasicPlayer so that the basic player knows its possible moving vectors.
    According to the number of vectors that this class in instantiated with, the angle spacing 
    and list of feasible move vectors are built.
    
    Main behavior is:
        - Building the list of feasible move vectors according to the last move vector of the player. 
'''

from basic_players import BasicPlayer
from vector_utils import VectorUtils
import numpy as np


class GuideVectorsPlayer(BasicPlayer):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._number_of_feasible_moving_vectors:int = kwargs.get('number_of_vectors', 8)
        
        # Initialize intrinsic variables
        self._angle_spacing:float = 2 * np.pi / self._number_of_feasible_moving_vectors
        self._feasible_move_vectors:list = []
    
    def get_feasible_move_vectors(self) -> list:
        return self._feasible_move_vectors
    
    def build_feasible_move_vectors(self) -> None:
        
        if (self._previous_move_vector == np.zeros((1,2))).all():
            base_vector = np.array([1,0]).reshape(1, -1)
        else:
            base_vector = VectorUtils.find_unit_vector(self._previous_move_vector)
        
        base_vector_angle = VectorUtils.find_vector_angle(base_vector)
        
        self._feasible_move_vectors = [
            VectorUtils.find_angle_vector(base_vector_angle + i * self._angle_spacing)
            for i in range(self._number_of_feasible_moving_vectors)
        ]
        
    def find_vector_deviations(self, unit_vector):
        return [
            VectorUtils.find_angle_between_two_vectors(unit_vector, move_vector)
            for move_vector in self._feasible_move_vectors
        ]