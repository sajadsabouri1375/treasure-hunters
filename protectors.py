from intelligent_players import IntelligentPlayer
from vector_utils import VectorUtils
import numpy as np
from copy import copy
from enum import Enum
from colorama import Fore

class ProtectorState(Enum):
    CAPTURING_HUNTER = 1
    RESCUING_TREASURE = 2
    CAPTURED_HUNTER = 3
    DEAD = 4
    LOST_TREASURE = 5

class Protector(IntelligentPlayer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (3.14-theta)/3.14)

        # Default values for a new protector
        self._is_alive = True
        self._hunter_last_position_in_sight = None
        self._number_of_not_in_sight_chasing = 0
        self._number_of_maximum_not_sight_chasing = kwargs.get('maximum_chase_time', 200)
        self._state = ProtectorState.CAPTURING_HUNTER
    
    def get_state(self):
        return self._state
    
    def get_state_string(self):
        if self._state == ProtectorState.CAPTURING_HUNTER:
            return f'{Fore.CYAN}Capturing{Fore.RESET}'
        elif self._state == ProtectorState.RESCUING_TREASURE:
            return f'{Fore.MAGENTA}Rescuing Treasure{Fore.RESET}'
        elif self._state == ProtectorState.CAPTURED_HUNTER:
            return f'{Fore.GREEN}Captured Hunter{Fore.RESET}'
        elif self._state == ProtectorState.DEAD:
            return f'{Fore.LIGHTRED_EX}Dead{Fore.RESET}'
        elif self._state == ProtectorState.LOST_TREASURE:
            return f'{Fore.RED}Lost{Fore.RESET}'
        
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
        
    def deduct_next_move(self, hunter, treasure, shelter, effective_distance):
        
        # Update state according to previous moves
        self.update_state(hunter, treasure, shelter, effective_distance)
                          
        if not self.shall_we_go_on():
            return
        
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
        if self._number_of_not_in_sight_chasing >= self._number_of_maximum_not_sight_chasing:
            self._hunter_last_position_in_sight = None
            self._number_of_not_in_sight_chasing = 0
            
        if hunter_distance == np.inf and self._hunter_last_position_in_sight is None:
            treasure_weight, hunter_weight = self.calculate_treasure_based_weights(False, hunter_treasure_distance)
            
        elif hunter_distance == np.inf and self._hunter_last_position_in_sight is not None and self._number_of_not_in_sight_chasing < self._number_of_maximum_not_sight_chasing:
            hunter.set_current_position(self._hunter_last_position_in_sight)
            hunter_distance, hunter_treasure_distance, hunter_move_vector = self.find_distance_and_move_vector_to(
                hunter,
                treasure,
                check_in_sight_status=False
            )
            treasure_weight, hunter_weight = self.calculate_treasure_based_weights(True, hunter_treasure_distance)
            self._number_of_not_in_sight_chasing += 1
               
        else:
            treasure_weight, hunter_weight = self.calculate_treasure_based_weights(True, hunter_treasure_distance)
            self._hunter_last_position_in_sight = copy(hunter.get_current_position())
            self._number_of_not_in_sight_chasing = 0
            
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

    def shall_we_go_on(self):

        if self._state in [ProtectorState.CAPTURING_HUNTER, ProtectorState.RESCUING_TREASURE]:
            return True
        return False
    
    def update_state(self, hunter, treasure, shelter, effective_distance):
        
        if not self.are_you_alive():
            self._state == ProtectorState.DEAD 
            return
    
        if self._state == ProtectorState.CAPTURING_HUNTER:
            if self.did_hunter_hunt_treasure(hunter, treasure, effective_distance):
                self._state = ProtectorState.RESCUING_TREASURE
                return
            
        if self._state == ProtectorState.RESCUING_TREASURE:
            if self.did_you_lose_treasure(hunter, shelter, effective_distance):
                self._state = ProtectorState.LOST_TREASURE
                return
        
        if self.did_you_capture_hunter(hunter, effective_distance):
            self._state = ProtectorState.CAPTURED_HUNTER
            return   
    
    def did_you_capture_hunter(self, hunter, effective_distance):
        
        if VectorUtils.find_distance_between_two_points(self.get_current_position(), hunter.get_current_position()) < effective_distance:
            return True
        return False
    
    def did_hunter_hunt_treasure(self, hunter, treasure, effective_distance):
        
        if VectorUtils.find_distance_between_two_points(hunter.get_current_position(), treasure.get_current_position()) < effective_distance:
            return True
        return False
    
    def did_you_lose_treasure(self, hunter, shelter, effective_distance):
        
        if VectorUtils.find_distance_between_two_points(hunter.get_current_position(), shelter.get_position()) < effective_distance:
            return True
        return False
    