from intelligent_players import IntelligentPlayer
from vector_utils import VectorUtils
import numpy as np
from copy import copy
from enum import Enum
from colorama import Fore

class GeneralHuntingState(Enum):
	HUNTING = 1							# Hunter is chasing treasure
	SHELTER = 2							# Hunter is returning to shelter

class DetailedHuntingState(Enum):
	DIRECT_HUNTING = 1                  # Hunter is chasing treasure and also considering a visible protector.
	INDIRECT_HUNTING = 2                # Hunter is chasing treasure and also considering a ghost protector.
	EASY_PEASY_HUNTING = 3              # Hunter is chasing treasure and there are no protectors (directly/indirectly) to interfere.
	DIRECT_SHELTER = 4                  # Hunter is returning to shelter and also considering a visible protector.
	INDIRECT_SHELTER = 5				# Hunter is returning to shelter and also considering a ghost protector.
	EASY_PEASY_SHELTER = 6				# Hunter is returning to shelter and there are no protectors (directly/indirectly) to interfere.
	
class HunterState(Enum):
	PLAYING = 1			                # Hunter has not successfully hunted treasure yet.
	CAPTURED = 5                        # Hunter is captured by the protector (whether before or after treasure is hunted).
	DEAD = 6                            # Hunter has hit a block.
	SAFE = 7                            # Hunter has hunted the treasure and returned to shelter safely without being captured.

class Hunter(IntelligentPlayer):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self._number_of_maximum_not_in_sight_escaping = kwargs.get('maximum_escape_time', 200)

		# Default values for a new hunter
		self._is_treasure_hunted = False
		self._is_hunter_arrested = False
		self._protector_last_position_in_sight = None
		self._number_of_not_in_sight_escaping = 0
		self._hunter_state = HunterState.PLAYING
		self._general_hunting_state = GeneralHuntingState.HUNTING
		self._detailed_hunting_state = None
		
	def get_hunter_state(self):
		return self._hunter_state

	def get_hunter_state_string(self):
		if self._hunter_state == HunterState.PLAYING and self._general_hunting_state == GeneralHuntingState.HUNTING:
			return f'{Fore.CYAN}Hunting{Fore.RESET}'
		elif self._hunter_state == HunterState.PLAYING and self._general_hunting_state == GeneralHuntingState.SHELTER:
			return f'{Fore.LIGHTGREEN_EX}Returning To Shelter{Fore.RESET}'
		elif self._hunter_state == HunterState.CAPTURED:
			return f'{Fore.RED}Captured By Protector{Fore.RESET}'
		elif self._hunter_state == HunterState.DEAD:
			return f'{Fore.LIGHTRED_EX}Dead{Fore.RESET}'
		elif self._hunter_state == HunterState.SAFE:
			return f'{Fore.GREEN}Safe{Fore.RESET}'
			 
	def deduct_next_move(self, protector, treasure, shelter, effective_distance):
		
		# Update hunting state
		self.update_hunting_state(protector, treasure, shelter, effective_distance)
  
		# Update hunter state
		self.update_hunter_state(protector, shelter, effective_distance)
		
		# If hunter is dead, captured, or safe, new moves are redundant.
		if not self.shall_we_go_on():
			return
		
		# Initiate feasible move vectors 
		self.build_feasible_move_vectors()
		
		# Filter move vectors which are too close to blocks
		self.filter_boundaries_move_vectors()
		
		# Calculate inertia effect weights
		self.calculate_inertia_weights()
		
		if self._general_hunting_state == GeneralHuntingState.HUNTING:
	  
			if self._detailed_hunting_state == DetailedHuntingState.DIRECT_HUNTING:
				
				# Update protector status (distance to treasure and move vector)
				protector_distance, protector_treasure_distance, protector_move_vector = self.find_distance_and_move_vector_to(protector, target='treasure')
				protector_move_vector = -1 * protector_move_vector
		
				treasure_weight, protector_weight = self.calculate_treasure_based_weights(protector_treasure_distance)
				self._protector_last_position_in_sight = copy(self.get_current_position())
				self._number_of_not_in_sight_escaping = 0
		
			elif self._detailed_hunting_state == DetailedHuntingState.INDIRECT_HUNTING:
		
				protector.set_current_position(self._protector_last_position_in_sight)
				protector_distance, protector_treasure_distance, protector_move_vector = self.find_distance_and_move_vector_to(protector, target='treasure')		
				protector_move_vector = -1 * protector_move_vector
				
				treasure_weight, protector_weight = self.calculate_treasure_based_weights(protector_treasure_distance)
				self._number_of_not_in_sight_escaping += 1
		
			elif self._detailed_hunting_state == DetailedHuntingState.EASY_PEASY_HUNTING:
				treasure_weight = 1
				protector_weight = 0
			
			# Apply treasure weight to guide vectors
			treasure_weights = self.find_treasure_move_vectors(treasure_weight)
		
			# Treasure protector guide vector
			if protector_weight > 0:
				protector_weights = self.find_other_player_move_vectors(protector_move_vector, protector_weight)
			else:
				protector_weights = np.zeros(self._number_of_feasible_moving_vectors)
			
			next_move_vector = self.find_max_score_move_vector(treasure_weights, protector_weights)

		if self._general_hunting_state == GeneralHuntingState.SHELTER:
			
			if self._detailed_hunting_state == DetailedHuntingState.DIRECT_SHELTER:
				
				# Update protector status (distance to treasure and move vector)
				protector_distance, protector_shelter_distance, protector_move_vector = self.find_distance_and_move_vector_to(protector, target='shelter')
				protector_move_vector = -1 * protector_move_vector
		
				shelter_weight, protector_weight = self.calculate_shelter_based_weights(protector_shelter_distance)
				self._protector_last_position_in_sight = copy(self.get_current_position())
				self._number_of_not_in_sight_escaping = 0
		
			elif self._detailed_hunting_state == DetailedHuntingState.INDIRECT_SHELTER:
		
				protector.set_current_position(self._protector_last_position_in_sight)
				protector_distance, protector_shelter_distance, protector_move_vector = self.find_distance_and_move_vector_to(protector, target='shelter')
				protector_move_vector = -1 * protector_move_vector
				
				shelter_weight, protector_weight = self.calculate_shelter_based_weights(protector_shelter_distance)
				self._number_of_not_in_sight_escaping += 1
		
			elif self._detailed_hunting_state == DetailedHuntingState.EASY_PEASY_SHELTER:
				shelter_weight = 1
				protector_weight = 0
	
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
		
		# Update distance to treasure and move vector towards treasure
		self.update_state_relative_to_treasure(treasure.get_current_position())   
		
		# Update distance to shelter and move vector towards shelter
		self.update_state_relative_to_shelter(shelter.get_position())  
	
	def update_hunting_state(self, protector, treasure, shelter, effective_distance):
	
		if self.did_you_capture_treasure(treasure, effective_distance):
			self._general_hunting_state = GeneralHuntingState.SHELTER

		# Update number of ghost protector escaping
		if self._number_of_not_in_sight_escaping >= self._number_of_maximum_not_in_sight_escaping:
			self._protector_last_position_in_sight = None
			self._number_of_not_in_sight_escaping = 0

		is_protector_in_sight = VectorUtils.are_points_in_sight(self.get_current_position(), protector.get_current_position(), self._map.get_boundaries())

		if self._general_hunting_state == GeneralHuntingState.HUNTING:
	  	
			if is_protector_in_sight:
				self._detailed_hunting_state = DetailedHuntingState.DIRECT_HUNTING
			elif not is_protector_in_sight and self._protector_last_position_in_sight is not None:
				self._detailed_hunting_state = DetailedHuntingState.INDIRECT_HUNTING
			else:
				self._detailed_hunting_state = DetailedHuntingState.EASY_PEASY_HUNTING
   
		elif self._general_hunting_state == GeneralHuntingState.SHELTER:
	  
			if is_protector_in_sight:
				self._detailed_hunting_state = DetailedHuntingState.DIRECT_SHELTER
			elif not is_protector_in_sight and self._protector_last_position_in_sight is not None:
				self._detailed_hunting_state = DetailedHuntingState.INDIRECT_SHELTER
			else:
				self._detailed_hunting_state = DetailedHuntingState.EASY_PEASY_SHELTER

	def update_hunter_state(self, protector, shelter, effective_distance):
		
		if not self.are_you_alive():
			self._hunter_state == HunterState.DEAD 
			return
	
		if self.are_you_captured(protector, effective_distance):
			self._hunter_state = HunterState.CAPTURED
			return
		
		if self._general_hunting_state == GeneralHuntingState.SHELTER:
			if self.did_you_make_it_to_shelter(shelter, effective_distance):
				self._hunter_state = HunterState.SAFE
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
	
	def shall_we_go_on(self):

		if self._hunter_state != HunterState.PLAYING:
			return False
		
		return True