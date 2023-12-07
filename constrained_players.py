from guide_vectors_players import GuideVectorsPlayer
import numpy as np
from vector_utils import VectorUtils

class ConstrainedPlayer(GuideVectorsPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._map = kwargs.get('map')
        self._boundaries_instruction = kwargs.get('boundaries_instruction')
    
    def get_feasible_move_vectors_distances(self):
        return self._feasible_move_vectors_distances
    
    def set_boundaries_instruction(self, new_instruction):
        self._boundaries_instruction = new_instruction
    
    def get_map(self):
        return self._map
        
    def calculate_distance_to_boundary(self, move_vector):
        move_vector_line = [
            self._current_position,
            self._current_position + move_vector * 100
        ]
        
        min_distance = np.inf
        for boundary in self._map.get_boundaries():
            intersection = VectorUtils.find_part_lines_intersection(boundary, move_vector_line)
            if intersection is None:
                continue
            if VectorUtils.is_point_on_part_line(boundary, intersection):
                distance = VectorUtils.find_distance_between_two_points(intersection, self._current_position)
                if distance < min_distance:
                    min_distance = distance
    
        return min_distance
                
    def build_feasible_move_vectors_distances(self):
        self._feasible_move_vectors_distances = [
            self.calculate_distance_to_boundary(move_vector)
            for move_vector in self._feasible_move_vectors
        ]
        
    def find_boundaries_move_vectors(self):
        self.build_feasible_move_vectors_distances()
        
        weights = [
            self._boundaries_instruction(distance)
            for distance in self._feasible_move_vectors_distances
        ]
        
        return weights
    
    def did_collide_with_boundaries(self):
        pass