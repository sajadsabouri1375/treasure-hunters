'''
    InertiaPlayer is a class which extends ConstrainedPlayer and would control the effect of
    inertia of the previous move vector on the next move vector.
    Note that the effect of inertia must not be too severe. It only should smoothen the movement of players 
    so that they appear more realistic.
    The evaluation of inertia effect is done by using the inertia formula given when instantiating the class.
'''

from constrained_players import ConstrainedPlayer
from vector_utils import VectorUtils
from maps import Map
import numpy as np

class InertiaPlayer(ConstrainedPlayer):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._inertia_instruction = kwargs.get('inertia_instruction', lambda deviation: 1)
        
        # Initialize class variables
        self._inertia_deviation_weights = []


    def calculate_inertia_weights(self):
        
        deviations = self.find_vector_deviations(self._previous_move_vector)
        
        self._inertia_deviation_weights = [
            self._inertia_instruction(deviation)
            for deviation in deviations
        ]