import unittest
from hunters import Hunter
from protectors import Protector
from treasure import Treasure
from shelter import Shelter
from optimized_maps import OptimizedMap
from drawing_assisstants import DrawingAssisstant
from controllers import Controller
import numpy as np


class TestHunters(unittest.TestCase):

    def setUp(cls):
        
        cls._treasure = Treasure(
            current_position=np.array([1.5, 0.85]).reshape(1, -1),
            is_hunted=False
        )
        
        cls._shelter = Shelter(
            position=np.array([1.5, 0.05]).reshape(1, -1)
        )
                
        cls._map = OptimizedMap(
            map_name='map_01',
            treasure=cls._treasure.get_current_position(),
            shelter=cls._shelter.get_position(),
            vertex_size = 0.05
        )
        cls._map.optimize_routes()
        
        cls._hunter = Hunter(
            step_size=0.01,
            current_position=np.array([1.1, 0.4]).reshape(1, -1),
            next_move_vector=np.array([-1, 0]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1/(1+theta),
            number_of_vectors=16,
            map=cls._map,
            boundaries_instruction=lambda distance: 1 / (1 + np.exp(max(-100 * (distance - 0.03), -700))),
            treasure_instruction=lambda relative_distance: np.exp(max(-0.01 * relative_distance, -700)),
            inertia_instruction = lambda deviation: np.exp(-0.1 * deviation),
            maximum_escape_time=20
        )
        
        cls._protector = Protector(
            step_size=0.01,
            current_position=np.array([1.3, 0.45]).reshape(1, -1),
            next_move_vector=np.array([-1, 0]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1/(1+theta),
            number_of_vectors=16,
            map=cls._map,
            boundaries_instruction=lambda distance: 1 / (1 + np.exp(max(-100 * (distance - 0.03), -700))),
            treasure_instruction=lambda relative_distance: np.exp(max(-1 * relative_distance, -700)),
            inertia_instruction = lambda deviation: np.exp(-0.1 * deviation),
            maximum_chase_time=40
        )
        
        cls._drawing_assisstant = DrawingAssisstant(
            map=cls._map,
            hunters=[cls._hunter],
            protectors=[cls._protector],
            treasure=cls._treasure,
            shelter=cls._shelter
        )
        
        cls._controller = Controller(
            hunter=cls._hunter,
            protector=cls._protector,
            treasure=cls._treasure,
            shelter=cls._shelter,
            map=cls._map,
            effective_distance=0.005,
            drawing_assisstant=cls._drawing_assisstant
        )
        
    def test_simulation(self):
        simulation_counter = 0
        while self._controller.shall_we_go_on():
            self._controller.simulate()
            self._controller.update_plot()
            simulation_counter += 1
        
        self._controller.report_simulation_status()
        
if __name__ == '__main__':
    unittest.main()
    