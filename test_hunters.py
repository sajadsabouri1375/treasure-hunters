import unittest
from hunters import Hunter
from basic_players import BasicPlayer
from treasure import Treasure
from maps import Map
import numpy as np
from vector_utils import VectorUtils


class TestHunters(unittest.TestCase):

    def setUp(cls):
        
        map = Map(map_name='map_box_01')
        
        cls._hunter = Hunter(
            step_size=0.1,
            next_move_vector=np.ones((1,2)),
            current_position=np.zeros((1,2)),
            velocity_reduction_inertia_formula=lambda theta: 1,
            number_of_vectors=8,
            map=map,
            boundaries_instruction=lambda distance: 1,
            treasure_hunt_instruction=lambda td_to_tptd: np.exp(-1 * td_to_tptd)
        )
        
        cls._treasure = Treasure(
            current_position=np.array([0.5, 0.5]).reshape(1, -1),
            is_hunted=False
        )
        
    def test_hunter_move_logic_hunting(self):
        self._hunter.set_current_position(np.array([0.25, 0.5]).reshape(1, -1))
        self._hunter.set_previous_move_vector(np.array([1, 0]).reshape(1, -1))
        protector = BasicPlayer(
            step_size=0.1,
            next_move_vector=np.ones((1,2)),
            current_position=np.array([0.95, 0.5]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1
        )
        
        initial_treasure_distance = VectorUtils.find_distance_between_two_points(self._hunter.get_current_position(), self._treasure.get_current_position())
        self._hunter.deduct_next_move(
            protector,
            self._treasure
        )
        final_treasure_distance = VectorUtils.find_distance_between_two_points(self._hunter.get_current_position(), self._treasure.get_current_position())
        
        self.assertLess(final_treasure_distance, initial_treasure_distance)
        
    def test_hunter_move_logic_escaping(self):
        self._hunter.set_current_position(np.array([0.05, 0.5]).reshape(1, -1))
        self._hunter.set_previous_move_vector(np.array([1, 0]).reshape(1, -1))
        protector = BasicPlayer(
            step_size=0.1,
            next_move_vector=np.ones((1,2)),
            current_position=np.array([0.55, 0.5]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1
        )
        
        initial_treasure_distance = VectorUtils.find_distance_between_two_points(self._hunter.get_current_position(), self._treasure.get_current_position())
        self._hunter.deduct_next_move(
            protector,
            self._treasure
        )
        final_treasure_distance = VectorUtils.find_distance_between_two_points(self._hunter.get_current_position(), self._treasure.get_current_position())
        
        self.assertGreater(final_treasure_distance, initial_treasure_distance)
        
if __name__ == '__main__':
    unittest.main()