import unittest
from constrained_players import ConstrainedPlayer
from maps import Map
import numpy as np


class TestPlayers(unittest.TestCase):

    def setUp(cls):
        
        map = Map(map_name='map_box_01')
        
        cls._player = ConstrainedPlayer(
            step_size=1,
            next_move_vector=np.ones((1,2)),
            current_position=np.zeros((1,2)),
            velocity_reduction_inertia_formula=lambda theta: 1,
            number_of_vectors=8,
            map=map
        )
        

    def test_discrete_player(self):
        
        self._player.set_previous_move_vector(np.ones((1,2)))
        
        self._player.build_feasible_move_vectors()
        
        feasible_move_vectors = self._player.get_feasible_move_vectors()
        
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(feasible_move_vectors[0][0,0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(feasible_move_vectors[0][0,1], 5))
        self.assertEqual(np.round(0, 5), np.round(feasible_move_vectors[1][0,0], 5))
        self.assertEqual(np.round(1, 5), np.round(feasible_move_vectors[1][0,1], 5))
        self.assertEqual(np.round(-1 * np.sqrt(2)/2, 5), np.round(feasible_move_vectors[2][0,0], 5))
        self.assertEqual(np.round(np.sqrt(2)/2, 5), np.round(feasible_move_vectors[2][0,1], 5))

    def test_distance_to_boundaries_calculation(self):
        
        self._player.set_current_position(np.array([0.5, 0.5]).reshape(1, -1))
        self._player.set_previous_move_vector(np.ones((1,2)))
        
        self._player.build_feasible_move_vectors()
        self._player.build_feasible_move_vectors_distances()
        
        distances = self._player.get_feasible_move_vectors_distances()
        
        self.assertEqual(np.round(np.sqrt(2)/2,5), np.round(distances[0], 5))
        self.assertEqual(np.round(0.5, 5), np.round(distances[1], 5))

if __name__ == '__main__':
    unittest.main()