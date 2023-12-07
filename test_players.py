import unittest
from players import Player
import numpy as np


class TestPlayers(unittest.TestCase):

    def setUp(cls):
        # First player velocity would not reduce due to inertia
        cls._first_player = Player(
            step_size=1,
            next_move_vector=np.ones((1,2)),
            current_position=np.zeros((1,2)),
            velocity_reduction_inertia_formula=lambda theta: 1,
            inertia_effect=0
        )
        
        # Second player velocity would reduct linearly due to inertia
        cls._second_player = Player(
            step_size=1,
            next_move_vector=np.ones((1,2)),
            current_position=np.zeros((1,2)),
            velocity_reduction_inertia_formula=lambda theta: 1 - (1/np.pi) * theta,
            inertia_effect=0
        )

    def test_first_player_movement(self):
        # First move from zero previous velocity 
        self._first_player.move()
        new_position = self._first_player.get_current_position()
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 1], 5))
        
        # Second move from a non-zero previous velocity 
        self._first_player.set_next_move_vector(np.array([1,0]).reshape(1, 2))
        self._first_player.move()
        new_position = self._first_player.get_current_position()
        self.assertEqual(np.round(1 + np.sqrt(2)/2, 5), np.round(new_position[0, 0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 1], 5))
        
    def test_second_player_movement(self):
        # First move from zero previous velocity 
        self._second_player.move()
        new_position = self._second_player.get_current_position()
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 1], 5))
        
        # Second move from a non-zero previous velocity 
        self._second_player.set_next_move_vector(np.array([1,0]).reshape(1, 2))
        self._second_player.move()
        new_position = self._second_player.get_current_position()
        self.assertEqual(np.round(0.75 + np.sqrt(2)/2, 5), np.round(new_position[0, 0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 1], 5))
        
        # Third move from a non-zero previous velocity 
        self._second_player.set_next_move_vector(np.array([-1,0]).reshape(1, 2))
        self._second_player.move()
        new_position = self._second_player.get_current_position()
        self.assertEqual(np.round(0.75 + np.sqrt(2)/2, 5), np.round(new_position[0, 0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(new_position[0, 1], 5))
        
if __name__ == '__main__':
    unittest.main()