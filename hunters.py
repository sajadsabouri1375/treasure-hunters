from intelligent_players import IntelligentPlayer
from vector_utils import VectorUtils
import numpy as np
from copy import copy
from enum import Enum
from colorama import Fore

class HunterState(Enum):
    HUNTING_TREASURE = 1
    RETURNING_TO_SHELTER = 2
    CAPTURED = 3
    DEAD = 4
    SAFE = 5

class Hunter(IntelligentPlayer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._number_of_maximum_not_sight_escaping = kwargs.get('maximum_escape_time', 200)

        # Default values for a new hunter
        self._is_treasure_hunted = False
        self._is_hunter_arrested = False
        self._protector_last_position_in_sight = None
        self._number_of_not_in_sight_escaping = 0
        self._state = HunterState.HUNTING_TREASURE
    
    def get_state(self):
        return self._state
    
    def get_state_string(self):
        if self._state == HunterState.HUNTING_TREASURE:
            return f'{Fore.CYAN}Hunting{Fore.RESET}'
        elif self._state == HunterState.RETURNING_TO_SHELTER:
            return f'{Fore.LIGHTGREEN_EX}Returning To Shelter{Fore.RESET}'
        elif self._state == HunterState.CAPTURED:
            return f'{Fore.RED}Captured By Protector{Fore.RESET}'
        elif self._state == HunterState.DEAD:
            return f'{Fore.LIGHTRED_EX}Dead{Fore.RESET}'
        elif self._state == HunterState.SAFE:
            return f'{Fore.GREEN}Safe{Fore.RESET}'
        
    def update_protector_status(self, protector):
        self._protector_distance, self._protector_move_vector = protector.get_distance_and_move_vector(self.get_current_position)

    def update_shelter_status(self, shelter):
        
        is_shelter_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), shelter.get_position(), self._map.get_boundaries())
        
        if not is_shelter_in_sight:
            self._shelter_distance, self._shelter_move_vector = self._map.get_distance_and_move_vector(self.get_current_position(), 'shelter')
            
        else:
            self._shelter_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), shelter.get_position())
            self._shelter_move_vector = shelter.get_position() - self.get_current_position()  
             
    def deduct_next_move(self, protector, treasure, shelter, effective_distance):
        
        # Update state according to the last state of the game
        self.update_state(protector, treasure, shelter, effective_distance)
        
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
            self.update_treasure_status(treasure.get_current_position())   
        
        # Update treasure status (distance and move vector)
        if self._shelter_distance is None:
            self.update_shelter_status(shelter)  
                      
        # Deduct weights
        if self._number_of_not_in_sight_escaping >= self._number_of_maximum_not_sight_escaping:
            self._protector_last_position_in_sight = None
            self._number_of_not_in_sight_escaping = 0
        
        if self._state == HunterState.HUNTING_TREASURE:
            
            # Update protector status (distance to treasure and move vector)
            protector_distance, protector_treasure_distance, protector_move_vector = self.find_distance_and_move_vector_to(protector, treasure)
        
            if protector_distance != np.inf:
                protector_move_vector = -1 * protector_move_vector
            
            if protector_distance == np.inf and self._protector_last_position_in_sight is None:
                treasure_weight = 1
                protector_weight = 0
                
            elif protector_distance == np.inf and self._protector_last_position_in_sight is not None and self._number_of_not_in_sight_escaping < self._number_of_maximum_not_sight_escaping:
                protector.set_current_position(self._protector_last_position_in_sight)
                protector_distance, protector_treasure_distance, protector_move_vector = self.find_distance_and_move_vector_to(
                    protector,
                    treasure,
                    check_in_sight_status=False
                )
                protector_move_vector = -1 * protector_move_vector
                treasure_weight, protector_weight = self.calculate_treasure_based_weights(protector_treasure_distance)
                self._number_of_not_in_sight_escaping += 1
                
            elif protector_distance != np.inf:
                treasure_weight, protector_weight = self.calculate_treasure_based_weights(protector_treasure_distance)
                self._protector_last_position_in_sight = copy(self.get_current_position())
                self._number_of_not_in_sight_escaping = 0
            
            # Apply treasure weight to guide vectors
            treasure_weights = self.find_treasure_move_vectors(treasure_weight)
        
            # Treasure protector guide vector
            if protector_weight > 0:
                protector_weights = self.find_other_player_move_vectors(protector_move_vector, protector_weight)
            else:
                protector_weights = np.zeros(self._number_of_feasible_moving_vectors)
            
            next_move_vector = self.find_max_score_move_vector(treasure_weights, protector_weights)

        if self._state == HunterState.RETURNING_TO_SHELTER:
            
            # Update protector status (distance to treasure and move vector)
            protector_distance, protector_shelter_distance, protector_move_vector = self.find_distance_and_move_vector_to_shelter(protector, shelter)
        
            if protector_distance != np.inf:
                protector_move_vector = -1 * protector_move_vector
                
            if protector_distance == np.inf and self._protector_last_position_in_sight is None:
                shelter_weight = 1
                protector_weight = 0
                
            elif protector_distance == np.inf and self._protector_last_position_in_sight is not None and self._number_of_not_in_sight_escaping < self._number_of_maximum_not_sight_escaping:
                protector.set_current_position(self._protector_last_position_in_sight)
                protector_distance, protector_shelter_distance, protector_move_vector = self.find_distance_and_move_vector_to_shelter(
                    protector,
                    shelter,
                    check_in_sight_status=False
                )
                protector_move_vector = -1 * protector_move_vector
                shelter_weight, protector_weight = self.calculate_shelter_based_weights(protector_shelter_distance)
                self._number_of_not_in_sight_escaping += 1
                
            elif protector_distance != np.inf:
                shelter_weight, protector_weight = self.calculate_shelter_based_weights(protector_shelter_distance)
                self._protector_last_position_in_sight = copy(self.get_current_position())
                self._number_of_not_in_sight_escaping = 0
            
            # Apply shelter weight to guide vectors
            shelter_weights = self.find_shelter_move_vectors(shelter_weight)
        
            # Treasure protector guide vector
            if protector_weight > 0:
                protector_weights = self.find_other_player_move_vectors(protector_move_vector, protector_weight)
            else:
                protector_weights = np.zeros(self._number_of_feasible_moving_vectors)
            
            next_move_vector = self.find_max_score_move_vector(shelter_weights, protector_weights)
            
        # Deduct next move vector according to all vectors
        self.set_next_move_vector(next_move_vector)
        self.move()

    def shall_we_go_on(self):

        if self._state in [HunterState.HUNTING_TREASURE, HunterState.RETURNING_TO_SHELTER]:
            return True
        
        return False
    
    def update_state(self, protector, treasure, shelter, effective_distance):
        
        if not self.are_you_alive():
            self._state == HunterState.DEAD 
            return
    
        if self.are_you_captured(protector, effective_distance):
            self._state = HunterState.CAPTURED
            return
            
        if not self._state == HunterState.RETURNING_TO_SHELTER:
            if self.did_you_capture_treasure(treasure, effective_distance):
                self._state = HunterState.RETURNING_TO_SHELTER
                return 
        
        if self._state == HunterState.RETURNING_TO_SHELTER:
            if self.did_you_make_it_to_shelter(shelter, effective_distance):
                self._state = HunterState.SAFE
                return    
    
    def did_you_capture_treasure(self, treasure, effective_distance):
        
        if VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure.get_current_position()) < effective_distance:
            return True
        return False

    def are_you_captured(self, protector, effective_distance):
        
        if VectorUtils.find_distance_between_two_points(self.get_current_position(), protector.get_current_position()) < effective_distance:
            return True
        return False
        
    def did_you_make_it_to_shelter(self, shelter, effective_distance):
        
        if VectorUtils.find_distance_between_two_points(self.get_current_position(), shelter.get_position()) < effective_distance:
            return True
        return False
    
            