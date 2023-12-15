import unittest
from hunters import Hunter
from protectors import Protector
from treasure import Treasure
from optimized_maps import OptimizedMap
from drawing_assisstants import DrawingAssisstant
from controllers import Controller
import numpy as np
from vector_utils import VectorUtils


class TestHunters(unittest.TestCase):

    def setUp(cls):
        
        cls._treasure = Treasure(
            current_position=np.array([1.5, 0.45]).reshape(1, -1),
            is_hunted=False
        )
                
        cls._map = OptimizedMap(
            map_name='map_01',
            point_of_interest=cls._treasure.get_current_position(),
            vertex_size = 0.05
        )
        cls._map.optimize_routes()
        
        cls._hunter = Hunter(
            step_size=0.01,
            current_position=np.array([0.45, 0.8]).reshape(1, -1),
            next_move_vector=np.array([1, 0]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1/(1+theta),
            number_of_vectors=32,
            map=cls._map,
            boundaries_instruction=lambda distance: 1 / (1 + np.exp(max(-100 * (distance - 0.08), -700))),
            treasure_instruction=lambda relative_distance: np.exp(max(-2 * relative_distance, -700)),
            inertia_instruction = lambda deviation: np.exp(-0.08 * deviation),
        )
        
        cls._protector = Protector(
            step_size=0.011,
            current_position=np.array([1.03, 0.36]).reshape(1, -1),
            next_move_vector=np.array([-1, 0]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1/(1+theta),
            number_of_vectors=32,
            map=cls._map,
            boundaries_instruction=lambda distance: 1 / (1 + np.exp(max(-100 * (distance - 0.08), -700))),
            treasure_instruction=lambda relative_distance: np.exp(max(-100 * relative_distance, -700)),
            inertia_instruction = lambda deviation: np.exp(-0.08 * deviation),
        )
        # np.exp(-5000000 * relative_distance)
        
        cls._drawing_assisstant = DrawingAssisstant(
            map=cls._map,
            hunters=[cls._hunter],
            protectors=[cls._protector],
            treasure=cls._treasure
        )
        
        cls._controller = Controller(
            hunter=cls._hunter,
            protector=cls._protector,
            treasure=cls._treasure,
            map=cls._map,
            effective_distance=0.005,
            drawing_assisstant=cls._drawing_assisstant
        )
        
    def test_simulation(self):
        simulation_counter = 0
        while not self._controller.is_simulation_done():
            self._controller.simulate()
            self._controller.update_plot()
            simulation_counter += 1
        
        self._controller.report_simulation_status()
        
if __name__ == '__main__':
    unittest.main()
    