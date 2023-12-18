from guide_vectors_players import GuideVectorsPlayer
import numpy as np
from vector_utils import VectorUtils

class ConstrainedPlayer(GuideVectorsPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._map = kwargs.get('map')
        self._boundaries_instruction = kwargs.get('boundaries_instruction')
        self._did_hit_the_boundaries = False
        self._feasible_move_vectors_distances = []

    def get_feasible_move_vectors_distances(self):
        return self._feasible_move_vectors_distances
    
    def get_map(self):
        return self._map
    
    def set_boundaries_instruction(self, new_instruction):
        self._boundaries_instruction = new_instruction
            
    def calculate_distance_to_boundary(self, move_vector_part_line):
                
        min_distance = np.inf
        for boundary in self._map.get_boundaries():
            
            intersection = VectorUtils.find_part_lines_intersection(boundary, move_vector_part_line)
            
            if intersection is None:
                continue
             
            distance = VectorUtils.find_distance_between_two_points(intersection, self._current_position)
            
            if distance < min_distance:
                min_distance = distance
    
        if min_distance == np.inf:
            print('hi')
            
        return min_distance
                
    def build_feasible_move_vectors_distances(self):
        self._feasible_move_vectors_distances = [
            self.calculate_distance_to_boundary(
                [
                    self._current_position,
                    self._current_position + move_vector * 100
                ]
            )
            for move_vector in self._feasible_move_vectors
        ]
        
    def filter_boundaries_move_vectors(self):
        
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
    
    def are_you_alive(self):
        
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
                 