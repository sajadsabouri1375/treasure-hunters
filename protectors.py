from intelligent_players import IntelligentPlayer
from vector_utils import VectorUtils
import numpy as np
from copy import copy


class Protector(IntelligentPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (np.pi-theta)/np.pi)
        self._is_alive = True
        self._hunter_last_position_in_sight = None
        
    def find_vector_deviations(self, unit_vector):
        return [
            VectorUtils.find_angle_between_two_vectors(unit_vector, move_vector)
            for move_vector in self._feasible_move_vectors
        ]
        
    def find_treasure_move_vectors(self, weight_treasure):
        
        treasure_unit_vector = VectorUtils.find_unit_vector(self._treasure_move_vector)
        
        self._feasible_move_vectors_treasure_deviations = self.find_vector_deviations(treasure_unit_vector)
        weights = [
            self._theta_effect(deviation) * weight_treasure
            for deviation in self._feasible_move_vectors_treasure_deviations
        ]
        return weights
          
    def find_treasure_hunter_move_vectors(self, treasure_hunter, wegith_treasure_protector):
        treasure_hunter_unit_vector = VectorUtils.find_unit_vector(+1 * (treasure_hunter.get_current_position() - self.get_current_position()))
        self._feasible_move_vectors_treasure_protector_deviations = self.find_vector_deviations(treasure_hunter_unit_vector)
        weights = [
            self._theta_effect(deviation) * wegith_treasure_protector
            for deviation in self._feasible_move_vectors_treasure_protector_deviations
        ]
        return weights
        
    def deduct_next_move(self, hunter, treasure):
        
        # Initiate feasible move vectors 
        self.build_feasible_move_vectors()
        
        # Filter move vectors which are too close to blocks
        self.filter_boundaries_move_vectors()
        
        # Calculate inertia effect weights
        self.calculate_inertia_based_weights()
        
        # Update treasure status (distance and move vector)
        if self._treasure_distance is None:
            self.update_treasure_status(treasure)   
            
        # Update hunter status
        hunter_distance, hunter_treasure_distance, hunter_move_vector = self.find_distance_and_move_vector_to(hunter, treasure)
        
        # Deduct weights
        if hunter_distance == np.inf and self._hunter_last_position_in_sight is None:
            treasure_weight, hunter_weight = self.calculate_treasure_based_weights(False, hunter_treasure_distance)
            
        elif hunter_distance == np.inf and self._hunter_last_position_in_sight is not None:
            hunter.set_current_position(self._hunter_last_position_in_sight)
            hunter_distance, hunter_treasure_distance, hunter_move_vector = self.find_distance_and_move_vector_to(hunter, treasure)
            
            if hunter_move_vector is not None:
                treasure_weight, hunter_weight = self.calculate_treasure_based_weights(True, hunter_treasure_distance)
            else:
                treasure_weight, hunter_weight = self.calculate_treasure_based_weights(False, hunter_treasure_distance)
                
        else:
            treasure_weight, hunter_weight = self.calculate_treasure_based_weights(True, hunter_treasure_distance)
            self._hunter_last_position_in_sight = copy(hunter.get_current_position())
        
        # Apply treasure weight to guide vectors
        treasure_weights = self.find_treasure_move_vectors(treasure_weight)
        
        # Treasure protector guide vector
        if hunter_weight > 0:
            hunter_weights = self.find_other_player_move_vectors(hunter_move_vector, hunter_weight)
        else:
            hunter_weights = np.zeros(self._number_of_feasible_moving_vectors)
            
        next_move_vector = self.find_max_score_move_vector(treasure_weights, hunter_weights)
        
        # Deduct next move vector according to all vectors
        self.set_next_move_vector(next_move_vector)
        self.move()
        self.update_status()