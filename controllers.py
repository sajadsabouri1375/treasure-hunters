from copy import deepcopy
from vector_utils import VectorUtils


class Controller:
    def __init__(self, **kwargs):
        self._hunter = kwargs.get('hunter')
        self._protector = kwargs.get('protector')
        self._treasure = kwargs.get('treasure')
        self._map = kwargs.get('map')
        self._effective_distance = kwargs.get('effective_distance', 0.01)
        self._drawing_assisstant = kwargs.get('drawing_assisstant')
        self._is_treasure_hunted = False
        self._is_hunter_captured = False
        self._max_simulation_steps = kwargs.get('max_simulation_steps', 2000)
        self._current_simulation_step = 0
        
    def simulate(self):
        hunter_copy = deepcopy(self._hunter)
        protector_copy = deepcopy(self._protector)
        
        self._hunter.deduct_next_move(protector_copy, self._treasure)
        self._protector.deduct_next_move(hunter_copy, self._treasure)
        
        self._current_simulation_step += 1
        self.update_status()
        
    def is_simulation_done(self):
        if self._is_hunter_captured or self._is_treasure_hunted or self._current_simulation_step >= self._max_simulation_steps:
            print(
                f'Simulation finished with:\nIs hunter captured: {self._is_hunter_captured}\nIs treasure hunted: {self._is_treasure_hunted}'
            )
            return True
        return False
    
    def update_status(self):
        if not self._is_treasure_hunted:
            if VectorUtils.find_distance_between_two_points(self._hunter.get_current_position(), self._treasure.get_current_position()) < self._effective_distance:
                self._is_treasure_hunted = True
        
        if not self._is_hunter_captured:
            if VectorUtils.find_distance_between_two_points(self._hunter.get_current_position(), self._protector.get_current_position()) < self._effective_distance:
                self._is_hunter_captured = True
    
    def update_plot(self):
        self._drawing_assisstant.update_plot()
        
        