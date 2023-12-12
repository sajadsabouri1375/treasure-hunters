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
            current_position=np.array([0.9, 0.9]).reshape(1, -1),
            is_hunted=False
        )
                
        cls._map = OptimizedMap(
            map_name='map_box_04',
            point_of_interest=cls._treasure.get_current_position(),
            vertex_size = 0.03
        )
        cls._map.optimize_routes()
        
        cls._hunter = Hunter(
            step_size=0.01,
            current_position=np.array([0.1, 0.5]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1/(1+theta),
            number_of_vectors=16,
            map=cls._map,
            boundaries_instruction=lambda distance: 1 / (1 + np.exp(-100 * (distance - 0.05))),
            treasure_instruction=lambda relative_distance: np.exp(-0.01 * relative_distance),
            inertia_effect = 0.25
        )
        
        cls._protector = Protector(
            step_size=0.01,
            current_position=np.array([0.9, 0.05]).reshape(1, -1),
            velocity_reduction_inertia_formula=lambda theta: 1/(1+theta),
            number_of_vectors=16,
            map=cls._map,
            boundaries_instruction=lambda distance: 1 / (1 + np.exp(-100 * (distance - 0.05))),
            treasure_instruction=lambda relative_distance: np.exp(-3 * relative_distance),
            inertia_effect = 0.25
        )
        
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
    