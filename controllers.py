from copy import deepcopy
from vector_utils import VectorUtils
from hunters import Hunter, HunterState, GeneralHuntingState
from protectors import Protector, ProtectorState, DetailedProtectingState
from drawing_assisstants import DrawingAssisstant
from enum import Enum
from colorama import Fore
import numpy as np

class GameDetailedState(Enum):
    TREASURE_HUNT = 1
    RETURNING_TO_SHELTER = 2
    HUNTER_IS_SAFE = 3
    HUNTER_IS_CAPTURED = 4
    EITHER_DEAD = 5
    
class GameGeneralState(Enum):
    HUNTER_WON = 1
    PROTECTOR_WON = 2
    IN_PROGRESS = 3
    DRAW = 4

class Controller:
    
    def __init__(self, **kwargs):
        
        self._hunters:list(Hunter) = kwargs.get('hunters')
        self._protector:Protector = kwargs.get('protector')
        self._treasure = kwargs.get('treasure')
        self._shelter = kwargs.get('shelter')
        self._map = kwargs.get('map')
        self._effective_distance = kwargs.get('effective_distance', 0.01)
        self._drawing_assisstant:DrawingAssisstant = kwargs.get('drawing_assisstant')
        self._max_simulation_steps = kwargs.get('max_simulation_steps', 500)

        # Default values for a new game
        self._current_simulation_step = 0
        self._game_general_state = GameGeneralState.IN_PROGRESS
        self._game_detailed_state = GameDetailedState.TREASURE_HUNT
        
        for hunter in self._hunters:
            hunter.initialize_player(self._treasure, self._shelter)
            
        self._protector.initialize_player(self._treasure, self._shelter)
        
    def get_state(self):
        return self._game_general_state
    
    def get_state_string(self):
        if self._game_general_state == GameGeneralState.HUNTER_WON:
            return f'{Fore.GREEN}Hunter Won{Fore.RESET}'
        elif self._game_general_state == GameGeneralState.PROTECTOR_WON:
            return f'{Fore.RED}Protector Won{Fore.RESET}'
        elif self._game_detailed_state == GameGeneralState.DRAW:
            return f'{Fore.LIGHTBLACK_EX}DRAW{Fore.RESET}'
        elif self._game_general_state == GameGeneralState.IN_PROGRESS:
            return f'{Fore.CYAN}In Progress{Fore.RESET}'
        
    def simulate(self):

        if not self.shall_we_go_on():
            return
        
        hunters_copy = list(filter(lambda item: True if item is not None else False, [deepcopy(hunter) if hunter.is_active() else None for hunter in self._hunters]))

        # Deduct hunter next move vector
        for hunter in self._hunters:
            if hunter.is_active():
                protector_copy = deepcopy(self._protector)
                hunter.deduct_next_move(protector_copy, self._treasure, self._shelter, self._effective_distance)
        
        # Deduct protector next move vector
        biggest_protector_move_vector = -1 * np.inf
        for hunter_copy in hunters_copy:
            
            if not hunter_copy.shall_we_go_on():
                continue
            
            protector_copy = deepcopy(self._protector)
            next_move_vector = protector_copy.deduct_next_move(deepcopy(hunter_copy), self._treasure, self._shelter, self._effective_distance)
            move_vector_size = np.linalg.norm(next_move_vector)
            
            if biggest_protector_move_vector == -1 * np.inf:
                biggest_protector_move_vector = move_vector_size
                candidate_hunter = hunter_copy
                
            else:
                
                if move_vector_size > biggest_protector_move_vector and protector_copy.get_protection_detailed_state() not in [DetailedProtectingState.ROAMING_SHELTER, DetailedProtectingState.ROAMING_TREASURE]:
                    biggest_protector_move_vector = move_vector_size
                    candidate_hunter = hunter_copy
        
        next_move_vector = self._protector.deduct_next_move(candidate_hunter, self._treasure, self._shelter, self._effective_distance)
        self._protector.apply_move(next_move_vector, self._treasure, self._shelter)
        
        # distances = [VectorUtils.find_distance_between_two_points(self._protector.get_current_position(), hunter.get_current_position()) if hunter.shall_we_go_on() else np.inf for hunter in self._hunters]
        
        # if len(distances) > 0:
        #     hunter_of_interest = self._hunters[np.argmin(np.array(distances))]
        #     next_move_vector = self._protector.deduct_next_move(deepcopy(hunter_of_interest), self._treasure, self._shelter, self._effective_distance)
        #     self._protector.apply_move(next_move_vector, self._treasure, self._shelter)
        
        self._current_simulation_step += 1
        
        self.synchronize_players_states()
        self.update_game_state()

    def synchronize_players_states(self):
        hunting_states = self.get_hunting_state()
        
        if any(hunting_state == GeneralHuntingState.SHELTER_WITH_TREASURE for hunting_state in hunting_states):
            
            for hunter in self._hunters:
                
                hunter.set_hunting_state(GeneralHuntingState.SHELTER)
                
                if hunter.get_hunting_general_state() == GeneralHuntingState.SHELTER_WITH_TREASURE:
                    
                    self._treasure.update_position(hunter.get_current_position())

            self._treasure.set_is_hunted(True)
            
    def report_simulation_status(self):
        print(
            f'''
            {Fore.BLUE}Players{Fore.RESET}:
                Hunter State: {", ".join([hunter.get_hunter_state_string() for hunter in self.get_active_hunters()])}
                Protector State: {self._protector.get_state_string()}
                
            {Fore.BLUE}Simulation finished with{Fore.RESET}:
                {self.get_state_string()}
            ''' 
        )
    
    def shall_we_go_on(self):
    
        if self._game_general_state != GameGeneralState.IN_PROGRESS or self._current_simulation_step >= self._max_simulation_steps:
            return False
        return True
    
    def get_active_hunters(self):
        return list(filter(lambda item: True if item is not None else False, [hunter if hunter.is_active() else None for hunter in self._hunters]))
        
    def get_hunters_states(self):
        return list(filter(lambda item: True if item is not None else False, [hunter.get_hunter_state() if hunter.is_active() else None for hunter in self._hunters]))
    
    def get_hunting_state(self):
        return list(filter(lambda item: True if item is not None else False, [hunter.get_hunting_general_state() if hunter.is_active() else None for hunter in self._hunters]))
    
    def update_game_state(self):
        hunters_states = self.get_hunters_states() 
        protector_state = self._protector.get_protector_state()
        
        if all([hunter_state == HunterState.DEAD for hunter_state in hunters_states]) and not protector_state == ProtectorState.DEAD:
            self._game_general_state = GameGeneralState.PROTECTOR_WON
            self._game_detailed_state = GameDetailedState.EITHER_DEAD
            
        elif any([hunter_state != HunterState.DEAD for hunter_state in hunters_states]) and protector_state == ProtectorState.DEAD:
            self._game_general_state = GameGeneralState.HUNTER_WON
            self._game_detailed_state = GameDetailedState.EITHER_DEAD

        elif all([hunter_state == HunterState.DEAD for hunter_state in hunters_states]) and protector_state == ProtectorState.DEAD:
            self._game_general_state = GameGeneralState.DRAW
            self._game_detailed_state = GameDetailedState.EITHER_DEAD
        
        elif all([hunter_state == HunterState.CAPTURED for hunter_state in hunters_states]):
            self._game_general_state = GameGeneralState.PROTECTOR_WON
            self._game_detailed_state = GameDetailedState.HUNTER_IS_CAPTURED
            
        elif any([hunter_state == HunterState.SAFE_WITH_TREASURE for hunter_state in hunters_states]):
            self._game_general_state = GameGeneralState.HUNTER_WON
            self._game_detailed_state = GameDetailedState.HUNTER_IS_SAFE
                     
    def update_plot(self, fix=False):
        self._drawing_assisstant.update_plot(fix)
        
        