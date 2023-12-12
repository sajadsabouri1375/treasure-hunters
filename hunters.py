from intelligent_players import IntelligentPlayer
from vector_utils import VectorUtils
import numpy as np


class Hunter(IntelligentPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._is_treasure_hunted = False
        self._is_hunter_arrested = False
        
    def update_protector_status(self, protector):
        self._protector_distance, self._protector_move_vector = protector.get_distance_and_move_vector(self.get_current_position)
                  
    def deduct_next_move(self, protector, treasure):
        
        # Initiate feasible move vectors 
        self.build_feasible_move_vectors()
        
        # Filter move vectors which are too close to blocks
        self.filter_boundaries_move_vectors()
        
        # Update treasure status (distance and move vector)
        if self._treasure_distance is None:
            self.update_treasure_status(treasure)   
            
        # Update protector status (distance to treasure and move vector)
        protector_distance, protector_treasure_distance, protector_move_vector = self.find_distance_and_move_vector_to(protector, treasure)
        
        if protector_distance != np.inf:
            protector_move_vector = -1 * protector_move_vector
        
        # Deduct weights
        treasure_weight, protector_weight = self.find_weights(protector_distance != np.inf, protector_treasure_distance)
        
        # Apply treasure weight to guide vectors
        treasure_weights = self.find_treasure_move_vectors(treasure_weight)
        
        # Treasure protector guide vector
        if protector_weight > 0:
            protector_weights = self.find_other_player_move_vectors(protector_move_vector, protector_weight)
        else:
            protector_weights = np.zeros(self._number_of_feasible_moving_vectors)
            
        next_move_vector = self.find_max_score_move_vector(treasure_weights, protector_weights)

        # Deduct next move vector according to all vectors
        self.set_next_move_vector(next_move_vector)
        self.move()
        self.update_status()
    
    def did_you_get_treasure(self, treasure, effective_distance):
        if not self._is_treasure_hunted:
            if VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure.get_current_position()) < effective_distance:
                self._is_treasure_hunted = True
        return self._is_treasure_hunted
                
    def did_protector_arrest_you(self, protector, effective_distance):
        if not self._is_hunter_arrested:
            if VectorUtils.find_distance_between_two_points(self.get_current_position(), protector.get_current_position()) < effective_distance:
                self._is_hunter_arrested = True
        return self._is_hunter_arrested
    
        