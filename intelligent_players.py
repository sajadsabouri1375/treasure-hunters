from constrained_players import ConstrainedPlayer
from vector_utils import VectorUtils
import numpy as np


class IntelligentPlayer(ConstrainedPlayer):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (np.pi-theta)/np.pi)
        self._treasure_instruction = kwargs.get('treasure_instruction')
        self._treasure_distance = None
        self._treasure_move_vector = None
        
    def reset_player(self):
        self._treasure_distance = None
        self._treasure_move_vector = None
        
    def find_vector_deviations(self, unit_vector):
        return [
            VectorUtils.find_angle_between_two_vectors(unit_vector, move_vector)
            for move_vector in self._feasible_move_vectors
        ]
        
    def find_treasure_move_vectors(self, weight_treasure):
        
        try:
            treasure_unit_vector = VectorUtils.find_unit_vector(self._treasure_move_vector)
            
            deviations = self.find_vector_deviations(treasure_unit_vector)
            
            ammortized_weights = [
                self._theta_effect(deviation) * weight_treasure
                for deviation in deviations
            ]
            
            return ammortized_weights
        
        except AttributeError:
            return np.zeros(len(self._feasible_move_vectors))    
    
    def find_other_player_move_vectors(self, other_player_move_vector, other_player_weight):
        
        other_player_unit_vector = VectorUtils.find_unit_vector(other_player_move_vector)
        
        diviations = self.find_vector_deviations(other_player_unit_vector)
        
        ammortized_weights = [
            self._theta_effect(deviation) * other_player_weight
            for deviation in diviations
        ]
        
        return ammortized_weights
    
    def find_distance_and_move_vector_to(self, player, treasure):
        
        is_player_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), player.get_current_position(), self._map.get_boundaries())
        # is_player_in_sight = True
        
        if is_player_in_sight:
            
            player_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), player.get_current_position())
            player_treasure_distance = player.get_treasure_distance(treasure)
            move_vector = player.get_current_position() - self.get_current_position()
            
        else:
            player_distance = np.inf
            player_treasure_distance = np.inf
            move_vector = None
        
        return player_distance, player_treasure_distance, move_vector

    def update_treasure_status(self, treasure):
        
        is_treasure_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), treasure.get_current_position(), self._map.get_boundaries())
        
        if not is_treasure_in_sight:
            self._treasure_distance, self._treasure_move_vector = self._map.get_distance_and_move_vector(self.get_current_position())
            
        else:
            self._treasure_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure.get_current_position())
            self._treasure_move_vector = treasure.get_current_position() - self.get_current_position()  
    
    def get_treasure_distance(self, treasure):
        if self._treasure_distance is not None:
            return self._treasure_distance
        else:
            self.update_treasure_status(treasure)
            return self._treasure_distance
        
    def find_weights(self, is_player_in_sight, player_distance):
        
        if is_player_in_sight:
            
            treasure_weight = self._treasure_instruction(
                self._treasure_distance / player_distance
            )
            player_weight = 1 - treasure_weight
        
        else:
            treasure_weight = 1
            player_weight = 0
            
        return treasure_weight, player_weight
    
    def find_max_score_move_vector(self, treasure_weights, other_player_weights):
        
        aggregate_move_vectors = [
            (treasure_weights[i] + other_player_weights[i]) * move_vector
            for i, move_vector in enumerate(self._feasible_move_vectors)
        ]
        
        aggregate_move_vectors_lengths = [
            np.linalg.norm(np.zeros((1, 2)) - move_vector)
            for move_vector in aggregate_move_vectors
        ]

        arg_max = max(range(len(aggregate_move_vectors_lengths)), key=aggregate_move_vectors_lengths.__getitem__)   
        next_move_vector = aggregate_move_vectors[arg_max if type(arg_max) is not list else arg_max[0]]
        
        return next_move_vector