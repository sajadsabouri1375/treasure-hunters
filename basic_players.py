'''
    Very basic behavior of all players would be implemented in this class. 
    This class has no dependency to player type.
    BasicPlayer only controls basic movements of players and has no intelligence 
    for deduction of new move vectors.
    This class is abstract and must not be initialized (Can be initialized for test purposes only).
    
    Main methods include:
        - reduction of step size (velocity) according to the level of orientation relative to
        previous move and the the formula given.
        - move method updates player position according to the new move vector which is set.
'''

from vector_utils import VectorUtils
import numpy as np
from numpy import array as npa
from abc import ABC

class BasicPlayer(ABC):
    
    def __init__(self, **kwargs):
        
        self._step_size:float = kwargs.get('step_size', 0)
        self._current_position:npa = kwargs.get('current_position', np.zeros((1,2)))
        self._next_move_vector:npa = kwargs.get('next_move_vector', np.zeros((1,2)))
        self._previous_position:npa = np.copy(self._current_position)
        self._previous_move_vector:npa = np.copy(self._next_move_vector)
        self._velocity_inertia_reduction_formula = kwargs.get('velocity_reduction_inertia_formula', lambda theta: 1)
        
    def get_current_position(self) -> npa:
        return self._current_position
    
    def get_previous_position(self) -> npa:
        return self._previous_position
    
    def set_next_move_vector(self, next_move_vector) -> None:
        if np.linalg.norm(next_move_vector) == 0:
            next_move_vector = self._previous_move_vector.copy()
        else:
            self._next_move_vector = next_move_vector
              
    def set_previous_move_vector(self, previous_move_vector) -> None:
        self._previous_move_vector = previous_move_vector
    
    def set_previous_position(self, previous_position) -> None:
        self._previous_position = previous_position
        
    def set_current_position(self, current_position) -> None:
        self._current_position = current_position
        
    def reduce_step_size(self) -> float:
        reduced_step_size = self._step_size * self._velocity_inertia_reduction_formula(
            VectorUtils.find_angle_between_two_vectors(
                self._previous_move_vector,
                self._next_move_vector
            )
        )
        return reduced_step_size
        
    def move(self) -> None:
        
        # Store the previous position and move vector which places player in the current position (previous move vector)
        self._previous_position = np.copy(self._current_position)
        
        # Deduct unit next move vector
        unit_next_move_vector = VectorUtils.find_unit_vector(self._next_move_vector)
        
        # Deduct step size according to inertia velocity reduction formula
        reduced_step_size = self.reduce_step_size()
        
        # Deduct new position
        self._current_position = self._current_position + unit_next_move_vector * reduced_step_size

        self._previous_move_vector = np.copy(unit_next_move_vector)
