import numpy as np
from vector_utils import VectorUtils

class Player:
    def __init__(self, **kwargs):
        self._step_size = kwargs.get('step_size', 0)
        self._current_position = kwargs.get('current_position', np.zeros((1,2)))
        self._next_move_vector = kwargs.get('next_move_vector', np.zeros((1,2)))
        self._previous_position = np.copy(self._current_position)
        self._previous_move_vector = np.zeros((1,2))
        self._velocity_inertia_reduction_formula = kwargs.get('velocity_reduction_inertia_formula', lambda tehta: 1)
        
    def get_current_position(self):
        return self._current_position
    
    def set_next_move_vector(self, next_move_vector):
        self._next_move_vector = next_move_vector
              
    def set_previous_move_vector(self, previous_move_vector):
        self._previous_move_vector = previous_move_vector
    
    def set_previous_position(self, previous_position):
        self._previous_position = previous_position
        
    def set_current_position(self, current_position):
        self._current_position = current_position
        
    def reduce_step_size(self):
        reduced_step_size = self._step_size * self._velocity_inertia_reduction_formula(
            VectorUtils.find_angle_between_two_vectors(
                self._previous_move_vector,
                self._next_move_vector
            )
        )
        return reduced_step_size
        
    def move(self):
        # Store the previous position and move vector which places player in the current position (previous move vector)
        self._previous_position = np.copy(self._current_position)
        
        # Deduct unit next move vector
        unit_next_move_vector = VectorUtils.find_unit_vector(self._next_move_vector)
        
        # Deduct step size according to inertia velocity reduction formula
        reduced_step_size = self.reduce_step_size()
        
        # Deduct new position
        self._current_position = self._current_position + unit_next_move_vector * reduced_step_size

        self._previous_move_vector = np.copy(self._next_move_vector)
