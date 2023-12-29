from copy import deepcopy
from vector_utils import VectorUtils
from hunters import Hunter, HunterState, GeneralHuntingState
from protectors import Protector, ProtectorState
from drawing_assisstants import DrawingAssisstant
from enum import Enum
from colorama import Fore

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
        self._hunter:Hunter = kwargs.get('hunter')
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
        self._hunter.initialize_player(self._treasure, self._shelter)
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
        
        hunter_copy = deepcopy(self._hunter)
        protector_copy = deepcopy(self._protector)
        
        self._hunter.deduct_next_move(protector_copy, self._treasure, self._shelter, self._effective_distance)
        self._protector.deduct_next_move(hunter_copy, self._treasure, self._shelter, self._effective_distance)
        
        self._current_simulation_step += 1
        self.update_game_state()
    
    def report_simulation_status(self):
        print(
            f'''
            {Fore.BLUE}Players{Fore.RESET}:
                Hunter State: {self._hunter.get_hunter_state_string()}
                Protector State: {self._protector.get_state_string()}
                
            {Fore.BLUE}Simulation finished with{Fore.RESET}:
                {self.get_state_string()}
            ''' 
        )
    
    def shall_we_go_on(self):
    
        if self._game_general_state != GameGeneralState.IN_PROGRESS or self._current_simulation_step >= self._max_simulation_steps:
            return False
        return True
    
    def update_game_state(self):
        hunter_state = self._hunter.get_hunter_state()
        protector_state = self._protector.get_protector_state()
        
        if hunter_state == HunterState.DEAD and not protector_state == ProtectorState.DEAD:
            self._game_general_state = GameGeneralState.PROTECTOR_WON
            self._game_detailed_state = GameDetailedState.EITHER_DEAD
            
        elif not hunter_state == HunterState.DEAD and protector_state == ProtectorState.DEAD:
            self._game_general_state = GameGeneralState.HUNTER_WON
            self._game_detailed_state = GameDetailedState.EITHER_DEAD

        elif hunter_state == HunterState.DEAD and protector_state == ProtectorState.DEAD:
            self._game_general_state = GameGeneralState.DRAW
            self._game_detailed_state = GameDetailedState.EITHER_DEAD
        
        elif hunter_state == HunterState.CAPTURED and protector_state == ProtectorState.CAPTURED:
            self._game_general_state = GameGeneralState.PROTECTOR_WON
            self._game_detailed_state = GameDetailedState.HUNTER_IS_CAPTURED
            
        elif hunter_state == HunterState.SAFE and protector_state == ProtectorState.LOST:
            self._game_general_state = GameGeneralState.HUNTER_WON
            self._game_detailed_state = GameDetailedState.HUNTER_IS_SAFE
                     
    def update_plot(self):
        self._drawing_assisstant.update_plot()
        
        