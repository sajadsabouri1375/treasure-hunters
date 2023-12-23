'''
    ConstrainedPlayer is a class which extends GuiveVectorsPlayer and would control the distances of
    each feasible move vector to the boundaries of the map.
    This class is able to filter feasible move vectors which are too close to the boundaries.
    The level of conservativity of collision with boundaries is controlled by the boundaries_instruction
    formula by which class is initialized.
    
    This class implements behaviors like:
        - Calculation of minimum distances of all feasible move vectors to boundaries and blocks of the map.
        - Filtering the feasible move vectors which are too close to blocks according to the boundaries_instruction
        formula.
'''

from guide_vectors_players import GuideVectorsPlayer
from vector_utils import VectorUtils
from maps import Map
import numpy as np

class ConstrainedPlayer(GuideVectorsPlayer):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._map:Map = kwargs.get('map')
        self._boundaries_instruction = kwargs.get('boundaries_instruction')
        
        # Initialize class variables
        self._did_hit_the_boundaries:bool = False
        self._feasible_move_vectors_distances:list = []

    def get_feasible_move_vectors_distances(self) -> list:
        return self._feasible_move_vectors_distances
    
    def get_map(self) -> Map:
        return self._map
    
    def set_boundaries_instruction(self, new_instruction) -> None:
        self._boundaries_instruction = new_instruction
            
    def calculate_distance_to_boundary(self, move_vector_part_line) -> float:
                
        min_distance = np.inf
        for boundary in self._map.get_boundaries():
            
            intersection = VectorUtils.find_part_lines_intersection(boundary, move_vector_part_line)
            
            if intersection is None:
                continue
             
            distance = VectorUtils.find_distance_between_two_points(intersection, self._current_position)
            
            if distance < min_distance:
                min_distance = distance
            
        return min_distance
                
    def build_feasible_move_vectors_distances(self) -> None:
        self._feasible_move_vectors_distances = [
            self.calculate_distance_to_boundary(
                [
                    self._current_position,
                    self._current_position + move_vector * 100
                ]
            )
            for move_vector in self._feasible_move_vectors
        ]
        
    def filter_boundaries_move_vectors(self) -> None:
        
        self.build_feasible_move_vectors_distances()
        
        strict_weights = [
            round(self._boundaries_instruction(distance))
            for distance in self._feasible_move_vectors_distances
        ]
        
        self._feasible_move_vectors = list(
            filter(
                lambda value: True if value is not None else False,
                [
                    move_vector if strict_weights[i] == 1 else None
                    for i, move_vector in enumerate(self._feasible_move_vectors)
                ]
            )
        )
    
    def are_you_alive(self) -> bool:
        
        previous_move_vector_line = [
            self.get_previous_position(),
            self.get_current_position()
        ]
    
        for boundary in self._map.get_boundaries():
            
            intersection = VectorUtils.find_part_lines_intersection(boundary, previous_move_vector_line)
            
            if intersection is None:
                continue
            else:
                return False
            
        return True
                 