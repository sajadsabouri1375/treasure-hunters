import unittest
from protectors import Protector
from basic_players import BasicPlayer
from treasure import Treasure
from maps import Map
import numpy as np
from vector_utils import VectorUtils


class TestProtectors(unittest.TestCase):

    def setUp(cls):
        
        map = Map(map_name='map_box_01')
        
        cls._protector = Protector(
            step_size=0.1,
            next_move_vector=np.ones((1,2)),
            current_position=np.zeros((1,2)),
            velocity_reduction_inertia_formula=lambda theta: 1,
            number_of_vectors=8,
            map=map,
            boundaries_instruction=lambda distance: 1,
            treasure_protection_instruction=lambda td_to_tptd: np.exp(-1 * td_to_tptd)
        )
        
        cls._treasure = Treasure(
            current_position=np.array([0.05, 0.5]).reshape(1, -1),
            is_hunted=False
        )
        
    def test_protector_move_logic_protection(self):
        self._protector.set_current_position(np.array([0.7, 0.5]).reshape(1, -1))
        self._protector.set_previous_move_vector(np.array([1, 0]).reshape(1, -1))
        hunter = BasicPlayer(
            step_size=0.1,
            next_move_vector=np.ones((1,2)),
            current_position=np.array([0.2, 0.2]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1
        )
        
        initial_treasure_distance = VectorUtils.find_distance_between_two_points(self._protector.get_current_position(), self._treasure.get_current_position())
        self._protector.deduct_next_move(
            hunter,
            self._treasure
        )
        final_treasure_distance = VectorUtils.find_distance_between_two_points(self._protector.get_current_position(), self._treasure.get_current_position())
        
        self.assertLess(final_treasure_distance, initial_treasure_distance)
        
    def test_protector_move_logic_capture(self):
        self._protector.set_current_position(np.array([0.5, 0.5]).reshape(1, -1))
        self._protector.set_previous_move_vector(np.array([1, 0]).reshape(1, -1))
        hunter = BasicPlayer(
            step_size=0.1,
            next_move_vector=np.ones((1,2)),
            current_position=np.array([0.7, 0.5]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1
        )
        
        initial_hunter_distance = VectorUtils.find_distance_between_two_points(self._protector.get_current_position(), hunter.get_current_position())
        self._protector.deduct_next_move(
            hunter,
            self._treasure
        )
        final_hunter_distance = VectorUtils.find_distance_between_two_points(self._protector.get_current_position(), hunter.get_current_position())
        
        self.assertLess(final_hunter_distance, initial_hunter_distance)
        
if __name__ == '__main__':
    unittest.main()