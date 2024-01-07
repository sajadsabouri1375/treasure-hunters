import numpy as np
from vector_utils import VectorUtils


class Treasure:
    def __init__(self, **kwargs):
        self._current_position = kwargs.get('current_position', np.zeros((1, 2)))
        self._cycling_radius = kwargs.get('cycling_radius', 0.05)
        self._cycling_positions = np.array(
            [
                [self._current_position[0,0], self._current_position[0,1]-self._cycling_radius],
                [self._current_position[0,0] + np.sqrt(3) / 2 * self._cycling_radius, self._current_position[0,1] + self._cycling_radius/2],
                [self._current_position[0,0] - np.sqrt(3) / 2 * self._cycling_radius, self._current_position[0,1] + self._cycling_radius/2]
            ]
        )
        self._current_wing_of_interest = 0
        self._is_hunted = False
        
    def set_is_hunted(self, is_hunted):
        self._is_hunted = is_hunted
        
    def get_is_hunted(self):
        return self._is_hunted
    
    def get_current_position(self):
        return self._current_position
    
    def get_cycling_radius(self):
        return self._cycling_radius
    
    def update_position(self, new_position):
        self._current_position = new_position
        
    def next_cycling_position(self):
        
        if self._current_wing_of_interest == self._cycling_positions.shape[0]-1:
            return 0
        else:
            return self._current_wing_of_interest + 1
            
    def get_closest_wing_position(self, object_position):
        
        wings_distance_sort_order = np.argsort(np.sum(np.square(self._cycling_positions - object_position), axis=1))
        
        if VectorUtils.find_distance_between_two_points(object_position, self._cycling_positions[self._current_wing_of_interest, :]) < 0.01:
            self._current_wing_of_interest = self.next_cycling_position()
            
        return self._cycling_positions[self._current_wing_of_interest, :]
    