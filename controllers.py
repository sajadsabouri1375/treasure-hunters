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
        self._is_hunter_arrested = False
        self._did_hunter_hit_the_boundaries = False
        self._did_protector_hit_the_boundaries = False
        self._max_simulation_steps = kwargs.get('max_simulation_steps', 500)
        self._current_simulation_step = 0
        
    def simulate(self):
        hunter_copy = deepcopy(self._hunter)
        protector_copy = deepcopy(self._protector)
        
        self._hunter.deduct_next_move(protector_copy, self._treasure)
        self._protector.deduct_next_move(hunter_copy, self._treasure)
        
        self._current_simulation_step += 1
        self.update_status()
        
    def is_simulation_done(self):
        if self._is_hunter_arrested or self._is_treasure_hunted or self._current_simulation_step >= self._max_simulation_steps or self._did_hunter_hit_the_boundaries or self._did_protector_hit_the_boundaries:
            return True
        return False
    
    def report_simulation_status(self):
        print(
            f'''
            Players:
                Hunter status: {'Dead' if self._did_hunter_hit_the_boundaries else 'Alive'}
                Protector status: {'Dead' if self._did_protector_hit_the_boundaries else 'Alive'}
                
            Simulation finished with:
                Is hunter arrested: {self._is_hunter_arrested}
                Is treasure hunted: {self._is_treasure_hunted}
            ''' 
        )
        
    def update_status(self):
        if not self._is_treasure_hunted:
            self._is_treasure_hunted = self._hunter.did_you_get_treasure(self._treasure, self._effective_distance)
        
        if not self._is_hunter_arrested:
            self._is_hunter_arrested = self._hunter.did_protector_arrest_you(self._protector, self._effective_distance)
    
        if not self._did_hunter_hit_the_boundaries:
            self._did_hunter_hit_the_boundaries = self._hunter.get_boundaries_hit_status()
        
        if not self._did_protector_hit_the_boundaries:
            self._did_protector_hit_the_boundaries = self._protector.get_boundaries_hit_status()

    def update_plot(self):
        self._drawing_assisstant.update_plot()
        
        