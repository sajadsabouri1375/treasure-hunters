'''
    IntelligentPlayer class extends InertiaPlayer class and implements the shared intelligence 
    amongst all types of players. For instance, updating treasure status for all players has the 
    same logic, so it would be implemented in this class.
'''

from inertia_players import InertiaPlayer
from vector_utils import VectorUtils
import numpy as np


class IntelligentPlayer(InertiaPlayer):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Theta effect formula distributes a given weight among all feasible move vectors. 
        # In case the deviation equals Pi, the ammortized weight must be zero.
        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (3.14-theta)/3.14)
        
        # Treasure instruction formula controls the weight of moving towards treasure according
        # to the ratio of distance to treasure to distance to protector
        self._treasure_instruction = kwargs.get('treasure_instruction')
        self._shelter_instruction = kwargs.get('shelter_instruction')
        
        # Initialize state variables for intelligent player class
        self._treasure_distance = None
        self._treasure_move_vector = None
        self._is_treasure_in_sight = None
        self._shelter_distance = None
        self._shelter_move_vector = None
        self._is_shelter_in_sight = None
    
    def initialize_player(self, treasure, shelter):
        self.update_state_relative_to_treasure(treasure.get_current_position())   
        self.update_state_relative_to_shelter(shelter.get_position()) 
    
    def get_treasure_distance(self):
        return self._treasure_distance
    
    def get_shelter_distance(self):
        return self._shelter_distance
    
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
    
    def find_shelter_move_vectors(self, shelter_weight):
        
        try:
            shelter_unit_vector = VectorUtils.find_unit_vector(self._shelter_move_vector)
            
            deviations = self.find_vector_deviations(shelter_unit_vector)
            
            ammortized_weights = [
                self._theta_effect(deviation) * shelter_weight
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
    
    def find_distance_and_move_vector_to(self, player, target = 'treasure'):
            
        player_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), player.get_current_position())
            
        if target == 'treasure':
            player_target_distance = player.get_treasure_distance()
                
        elif target == 'shelter':
            player_target_distance = player.get_shelter_distance()
                
        move_vector = player.get_current_position() - self.get_current_position()
            
        return player_distance, player_target_distance, move_vector
    
    def find_distance_and_move_vector_towards_landmark(self, landmark_position, landmark_type):
        
        is_landmark_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), landmark_position, self._map.get_boundaries())
        
        if not is_landmark_in_sight:
            distance_to_landmark, move_vector_to_landmark = self._map.get_distance_and_move_vector(self.get_current_position(), landmark_type)
            
        else:
            distance_to_landmark = VectorUtils.find_distance_between_two_points(self.get_current_position(), landmark_position)
            move_vector_to_landmark = landmark_position - self.get_current_position() 
        
        return distance_to_landmark, move_vector_to_landmark, is_landmark_in_sight
    
    def update_state_relative_to_treasure(self, treasure_position):
        
        self._treasure_distance, self._treasure_move_vector, self._is_treasure_in_sight = self.find_distance_and_move_vector_towards_landmark(treasure_position, 'treasure')
        
    def update_state_relative_to_shelter(self, shelter_position):
        
        self._shelter_distance, self._shelter_move_vector, self._is_shelter_in_sight = self.find_distance_and_move_vector_towards_landmark(shelter_position, 'shelter')
        
    def calculate_treasure_based_weights(self, player_distance):
        
        treasure_weight = self._treasure_instruction(
            self._treasure_distance / player_distance
        )
        player_weight = 1 - treasure_weight
            
        return treasure_weight, player_weight
    
    def calculate_shelter_based_weights(self, player_distance):
        
        shelter_weight = self._shelter_instruction(
            self._shelter_distance / player_distance
        )
        player_weight = 1 - shelter_weight
            
        return shelter_weight, player_weight
    
    def find_max_score_move_vector(self, treasure_weights, other_player_weights):
        
        aggregate_weights = [
            (treasure_weights[i] + other_player_weights[i]) * self._inertia_deviation_weights[i]
            for i, move_vector in enumerate(self._feasible_move_vectors)
        ]

        arg_max = max(range(len(aggregate_weights)), key=aggregate_weights.__getitem__)   
        next_move_vector = self._feasible_move_vectors[arg_max if type(arg_max) is not list else arg_max[0]]
        
        return next_move_vector
    
        
        