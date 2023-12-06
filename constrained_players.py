from players import Player
import numpy as np
from vector_utils import VectorUtils

class ConstrainedPlayer(Player):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._map = kwargs.get('map')
        self._boundaries_instruction = kwargs.get('boundaries_instruction')
        self._number_of_feasible_moving_vectors = kwargs.get('number_of_vectors', 8)
        self._angle_spacing = 2 * np.pi / self._number_of_feasible_moving_vectors
        self._feasible_move_vectors = []
        self._feasible_move_vectors_distances = []
    
    def get_feasible_move_vectors(self):
        return self._feasible_move_vectors
    
    def get_feasible_move_vectors_distances(self):
        return self._feasible_move_vectors_distances
    
    def set_boundaries_instruction(self, new_instruction):
        self._boundaries_instruction = new_instruction
    
    def get_map(self):
        return self._map
    
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
        
    def find_boundaries_move_vector(self):
        self.build_feasible_move_vectors()
        self.build_feasible_move_vectors_distances()
        
        weights = [
            self._boundaries_instruction(distance)
            for distance in self._feasible_move_vectors_distances
        ]
        
        weighted_feasible_move_vectors = [
            weight * move_vector
            for (weight, move_vector) in zip(weights, self._feasible_move_vectors)
        ]
        
        selected_vector = np.array(weighted_feasible_move_vectors).reshape(self._number_of_feasible_moving_vectors, 2).sum(axis=0)
        return selected_vector