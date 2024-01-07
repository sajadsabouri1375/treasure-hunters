from intelligent_players import IntelligentPlayer
from vector_utils import VectorUtils
import numpy as np
from copy import copy
from enum import Enum
from colorama import Fore
from hunters import GeneralHuntingState

class GeneralProtectionState(Enum):
    PROTECTING = 1							# Protector is protecting treasure
    RESCUING = 2							# Protector is rescuing treasure

class DetailedProtectingState(Enum):
    DIRECT_PROTECTING = 1                   # Protector is chasing treasure and also considering a visible protector.
    INDIRECT_PROTECTING = 2                 # Protector is chasing treasure and also considering a ghost protector.
    ROAMING_TREASURE = 3                    # Protector is chasing treasure and there are no protectors (directly/indirectly) to interfere.
    DIRECT_RESCUING = 4                     # Protector is returning to shelter and also considering a visible protector.
    INDIRECT_RESCUING = 5		    	    # Protector is returning to shelter and also considering a ghost protector.
    ROAMING_SHELTER = 6						
 
class ProtectorState(Enum):
    PLAYING = 1			                    # Protector has not successfully captured treasure yet.
    CAPTURED = 2                            # Protector has captured hunter whether treasure is hunted or not.
    DEAD = 3                                # Protector has hit a block.
    LOST = 4                                # Protector has missed the hunter and hunter is at safety with treasure hunted.
 
class Protector(IntelligentPlayer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (3.14-theta)/3.14)

        # Default values for a new protector
        self._is_alive = True
        self._hunter_last_position_in_sight = None
        self._number_of_not_in_sight_chasing = 0
        self._number_of_maximum_not_in_sight_chasing = kwargs.get('maximum_chase_time', 200)
        self._protector_state = ProtectorState.PLAYING
        self._general_protection_state = GeneralProtectionState.PROTECTING
        self._detailed_protection_state = None
    
    def get_protector_state(self):
        return self._protector_state
    
    def get_state_string(self):
        if self._protector_state == ProtectorState.PLAYING and self._general_protection_state == GeneralProtectionState.PROTECTING:
            return f'{Fore.CYAN}Capturing{Fore.RESET}'
        elif self._protector_state == ProtectorState.PLAYING and self._general_protection_state == GeneralProtectionState.RESCUING:
            return f'{Fore.MAGENTA}Rescuing Treasure{Fore.RESET}'
        elif self._protector_state == ProtectorState.CAPTURED:
            return f'{Fore.GREEN}Captured Hunter{Fore.RESET}'
        elif self._protector_state == ProtectorState.DEAD:
            return f'{Fore.LIGHTRED_EX}Dead{Fore.RESET}'
        elif self._protector_state == ProtectorState.LOST:
            return f'{Fore.RED}Lost{Fore.RESET}'
        
    def get_protection_general_state(self):
        return self._general_protection_state
      
    def get_protection_detailed_state(self):
        return self._detailed_protection_state
    
    def deduct_next_move(self, hunter, treasure, shelter, effective_distance):
        
        # Update number of ghost hunter chasing
        if self._number_of_not_in_sight_chasing >= self._number_of_maximum_not_in_sight_chasing:
            self._hunter_last_position_in_sight = None
            self._number_of_not_in_sight_chasing = 0
            
        # Update protection state
        self.update_protection_state(hunter, treasure, shelter, effective_distance)
        
        # Update state according to previous moves
        self.update_protector_state(hunter, shelter, effective_distance)
                          
        if not self.shall_we_go_on():
            return
        
        # Initiate feasible move vectors 
        self.build_feasible_move_vectors()
        
        # Filter move vectors which are too close to blocks
        self.filter_boundaries_move_vectors()
        
        # Calculate inertia effect weights
        self.calculate_inertia_weights()
        
        if self._general_protection_state == GeneralProtectionState.PROTECTING:
            
            if self._detailed_protection_state == DetailedProtectingState.DIRECT_PROTECTING:
                hunter_distance, hunter_treasure_distance, hunter_move_vector = self.find_distance_and_move_vector_to(hunter, target='treasure')
                treasure_weight, hunter_weight = self.calculate_treasure_based_weights(hunter_treasure_distance)
                self._hunter_last_position_in_sight = copy(hunter.get_current_position())
                self._number_of_not_in_sight_chasing = 0
    
            elif self._detailed_protection_state == DetailedProtectingState.INDIRECT_PROTECTING:
                
                hunter.set_current_position(self._hunter_last_position_in_sight)
                hunter_distance, hunter_treasure_distance, hunter_move_vector = self.find_distance_and_move_vector_to(hunter, target='treasure')
                treasure_weight, hunter_weight = self.calculate_treasure_based_weights(hunter_treasure_distance)
                self._number_of_not_in_sight_chasing += 1
        
            elif self._detailed_protection_state == DetailedProtectingState.ROAMING_TREASURE:
                
                if self._is_treasure_in_sight:
                    self.update_state_relative_to_treasure(treasure.get_closest_wing_position(self.get_current_position()))
                
                treasure_weight = 1
                hunter_weight = 0
    
              # Apply treasure weight to guide vectors
            treasure_weights = self.find_treasure_move_vectors(treasure_weight)
            
            # Treasure protector guide vector
            if hunter_weight > 0:
                hunter_weights = self.find_other_player_move_vectors(hunter_move_vector, hunter_weight)
            else:
                hunter_weights = np.zeros(self._number_of_feasible_moving_vectors)
                
            next_move_vector = self.find_max_score_move_vector(treasure_weights, hunter_weights)
   
        elif self._general_protection_state == GeneralProtectionState.RESCUING:
            
            if self._detailed_protection_state == DetailedProtectingState.DIRECT_RESCUING:
       
                # Update protector status (distance to treasure and move vector)
                hunter_distance, hunter_shelter_distance, hunter_move_vector = self.find_distance_and_move_vector_to(hunter, target='shelter')
        
                shelter_weight, hunter_weight = self.calculate_shelter_based_weights(hunter_shelter_distance)
                self._hunter_last_position_in_sight = copy(self.get_current_position())
                self._number_of_not_in_sight_chasing = 0
    
            elif self._detailed_protection_state == DetailedProtectingState.INDIRECT_RESCUING:
       
                hunter.set_current_position(self._hunter_last_position_in_sight)
                hunter_distance, hunter_shelter_distance, hunter_move_vector = self.find_distance_and_move_vector_to(hunter, target='shelter')
                
                shelter_weight, hunter_weight = self.calculate_shelter_based_weights(hunter_shelter_distance)
                self._number_of_not_in_sight_chasing += 1
        
            elif self._detailed_protection_state == DetailedProtectingState.ROAMING_SHELTER:
                shelter_weight = 1
                hunter_weight = 0
    
            # Apply shelter weight to guide vectors
            shelter_weights = self.find_shelter_move_vectors(shelter_weight)
        
            # Treasure protector guide vector
            if hunter_weight > 0:
                hunter_weights = self.find_other_player_move_vectors(hunter_move_vector, hunter_weight)
            else:
                hunter_weights = np.zeros(self._number_of_feasible_moving_vectors)
            
            next_move_vector = self.find_max_score_move_vector(shelter_weights, hunter_weights)
        
        # Update protection state
        self.update_protection_state(hunter, treasure, shelter, effective_distance)
        
        # Update state according to previous moves
        self.update_protector_state(hunter, shelter, effective_distance) 
        
        return next_move_vector

    def apply_move(self, next_move_vector, treasure, shelter):
     
        # Deduct next move vector according to all vectors
        self.set_next_move_vector(next_move_vector)
        self.move()
    
         # Update distance to treasure and move vector towards treasure
        self.update_state_relative_to_treasure(treasure.get_current_position())   
        
        # Update distance to shelter and move vector towards shelter
        self.update_state_relative_to_shelter(shelter.get_position()) 
  
    def update_protection_state(self, hunter, treasure, shelter, effective_distance):
        
        if hunter.get_hunting_general_state() == GeneralHuntingState.SHELTER:
            self._general_protection_state = GeneralProtectionState.RESCUING

        is_hunter_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), hunter.get_current_position(), self._map.get_boundaries())

        if self._general_protection_state == GeneralProtectionState.PROTECTING:
          
            if is_hunter_in_sight:
                self._detailed_protection_state = DetailedProtectingState.DIRECT_PROTECTING
            elif not is_hunter_in_sight and self._hunter_last_position_in_sight is not None:
                self._detailed_protection_state = DetailedProtectingState.INDIRECT_PROTECTING
            else:
                self._detailed_protection_state = DetailedProtectingState.ROAMING_TREASURE
   
        elif self._general_protection_state == GeneralProtectionState.RESCUING:
      
            if is_hunter_in_sight:
                self._detailed_protection_state = DetailedProtectingState.DIRECT_RESCUING
            elif not is_hunter_in_sight and self._hunter_last_position_in_sight is not None:
                self._detailed_protection_state = DetailedProtectingState.INDIRECT_RESCUING
            else:
                self._detailed_protection_state = DetailedProtectingState.ROAMING_SHELTER
        
    def update_protector_state(self, hunter, shelter, effective_distance):
        
        if not self.are_you_alive():
            self._protector_state == ProtectorState.DEAD 
            return
            
        if self._general_protection_state == GeneralProtectionState.RESCUING:
            if self.did_you_lose_treasure(hunter, shelter, effective_distance):
                self._protector_state = ProtectorState.LOST
                return
        
        if self.did_you_capture_hunter(hunter, effective_distance):
            self._protector_state = ProtectorState.CAPTURED
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
    
    def shall_we_go_on(self):

        if self._protector_state in [ProtectorState.PLAYING, ProtectorState.CAPTURED]:
            return True

        return False