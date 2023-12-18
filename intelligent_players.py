from constrained_players import ConstrainedPlayer
from vector_utils import VectorUtils
import numpy as np


class IntelligentPlayer(ConstrainedPlayer):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (np.pi-theta)/np.pi)
        self._treasure_instruction = kwargs.get('treasure_instruction')
        self._inertia_instruction = kwargs.get('inertia_instruction', lambda deviation: 1)
        self._treasure_distance = None
        self._treasure_move_vector = None
        self._shelter_distance = None
        self._shelter_move_vector = None
        self._inertia_deviation_weights = []
        
    def reset_player(self):
        self._treasure_distance = None
        self._treasure_move_vector = None
        self._shelter_distance = None
        self._shelter_move_vector = None
        
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
    
    def find_distance_and_move_vector_to(self, player, treasure, check_in_sight_status=True):
        
        if check_in_sight_status:
            is_player_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), player.get_current_position(), self._map.get_boundaries())
        else:
            is_player_in_sight = True
            
        if is_player_in_sight:
            
            player_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), player.get_current_position())
            player_treasure_distance = player.get_treasure_distance(treasure)
            move_vector = player.get_current_position() - self.get_current_position()
            
        else:
            player_distance = np.inf
            player_treasure_distance = np.inf
            move_vector = None
        
        return player_distance, player_treasure_distance, move_vector

    def find_distance_and_move_vector_to_shelter(self, player, shelter, check_in_sight_status=True):
        
        if check_in_sight_status:
            is_player_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), player.get_current_position(), self._map.get_boundaries())
        else:
            is_player_in_sight = True
            
        if is_player_in_sight:
            
            player_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), player.get_current_position())
            player_shelter_distance = player.get_shelter_distance(shelter)
            move_vector = player.get_current_position() - self.get_current_position()
            
        else:
            player_distance = np.inf
            player_shelter_distance = np.inf
            move_vector = None
        
        return player_distance, player_shelter_distance, move_vector
    
    def update_treasure_status(self, treasure):
        
        is_treasure_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), treasure.get_current_position(), self._map.get_boundaries())
        
        if not is_treasure_in_sight:
            self._treasure_distance, self._treasure_move_vector = self._map.get_distance_and_move_vector(self.get_current_position(), 'treasure')
            
        else:
            self._treasure_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure.get_current_position())
            self._treasure_move_vector = treasure.get_current_position() - self.get_current_position()  
    
    def update_shelter_status(self, shelter):
        
        is_shelter_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), shelter.get_position(), self._map.get_boundaries())
        
        if not is_shelter_in_sight:
            self._shelter_distance, self._shelter_move_vector = self._map.get_distance_and_move_vector(self.get_current_position(), 'shelter')
            
        else:
            self._shelter_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), shelter.get_position())
            self._shelter_move_vector = shelter.get_position() - self.get_current_position()  
            
    def get_treasure_distance(self, treasure):
        if self._treasure_distance is not None:
            return self._treasure_distance
        else:
            self.update_treasure_status(treasure)
            return self._treasure_distance
    
    def get_shelter_distance(self, shelter):
        if self._shelter_distance is not None:
            return self._shelter_distance
        else:
            self.update_shelter_status(shelter)
            return self._shelter_distance
        
    def calculate_treasure_based_weights(self, is_player_in_sight, player_distance):
        
        if is_player_in_sight:
            
            treasure_weight = self._treasure_instruction(
                self._treasure_distance / player_distance
            )
            player_weight = 1 - treasure_weight
        
        else:
            treasure_weight = 1
            player_weight = 0
            
        return treasure_weight, player_weight
    
    def calculate_shelter_based_weights(self, is_player_in_sight, player_distance):
        
        if is_player_in_sight:
            
            shelter_weight = self._treasure_instruction(
                self._shelter_distance / player_distance
            )
            player_weight = 1 - shelter_weight
        
        else:
            shelter_weight = 1
            player_weight = 0
            
        return shelter_weight, player_weight
    
    def find_max_score_move_vector(self, treasure_weights, other_player_weights):
        
        aggregate_weights = [
            (treasure_weights[i] + other_player_weights[i]) * self._inertia_deviation_weights[i]
            for i, move_vector in enumerate(self._feasible_move_vectors)
        ]

        arg_max = max(range(len(aggregate_weights)), key=aggregate_weights.__getitem__)   
        next_move_vector = self._feasible_move_vectors[arg_max if type(arg_max) is not list else arg_max[0]]
        
        return next_move_vector
    
    def calculate_inertia_based_weights(self):
        
        deviations = self.find_vector_deviations(self._previous_move_vector)
        
        self._inertia_deviation_weights = [
            self._inertia_instruction(deviation)
            for deviation in deviations
        ]
        
        