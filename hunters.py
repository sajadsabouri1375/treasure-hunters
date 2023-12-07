from constrained_players import ConstrainedPlayer
from vector_utils import VectorUtils
import numpy as np


class Hunter(ConstrainedPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._treasure_hunt_instruction = kwargs.get('treasure_hunt_instruction')
        self._theta_effect = kwargs.get('deviation_effect', lambda theta: (np.pi-theta)/np.pi)
        
    def find_vector_deviations(self, unit_vector):
        return [
            VectorUtils.find_angle_between_two_vectors(unit_vector, move_vector)
            for move_vector in self._feasible_move_vectors
        ]
        
    def find_treasure_move_vectors(self, treasure, weight_treasure):
        treasure_unit_vector = VectorUtils.find_unit_vector(treasure.get_current_position() - self.get_current_position())
        self._feasible_move_vectors_treasure_deviations = self.find_vector_deviations(treasure_unit_vector)
        weights = [
            self._theta_effect(deviation) * weight_treasure
            for deviation in self._feasible_move_vectors_treasure_deviations
        ]
        return weights
        
    def find_treasure_protector_move_vectors(self, treasure_protector, wegith_treasure_protector):
        treasure_protector_unit_vector = VectorUtils.find_unit_vector(-1 * (treasure_protector.get_current_position() - self.get_current_position()))
        self._feasible_move_vectors_treasure_protector_deviations = self.find_vector_deviations(treasure_protector_unit_vector)
        weights = [
            self._theta_effect(deviation) * wegith_treasure_protector
            for deviation in self._feasible_move_vectors_treasure_protector_deviations
        ]
        return weights
        
    def deduct_next_move(self, treasure_protector, treasure):
        
        self.build_feasible_move_vectors()
        
        # Deduct boundaries move vector using constrained player parent
        boundaries_weights = self.find_boundaries_move_vectors()
        
        # Deduct treasure and treasure protector weight distribution
        treasure_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure.get_current_position())
        
        is_treasure_protector_in_sight = VectorUtils.are_poits_in_sight(self.get_current_position(), treasure_protector.get_current_position(), self._map.get_boundaries())
        if is_treasure_protector_in_sight:
            # TODO -> Treasure protector distance must be in equations somewhere in the future formulation!
            treasure_protector_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure_protector.get_current_position())
            treasure_protector_treasure_distance = VectorUtils.find_distance_between_two_points(treasure.get_current_position(), treasure_protector.get_current_position())

            weight_treasure = self._treasure_hunt_instruction(
                treasure_distance / treasure_protector_treasure_distance
            )
            weight_treasure_protector = 1 - weight_treasure
        
        else:
            weight_treasure = 1
            weight_treasure_protector = 0
            
        # Treasure guide vector
        treasure_weights = self.find_treasure_move_vectors(treasure, weight_treasure)
        
        # Treasure protector guide vector
        if is_treasure_protector_in_sight:
            treasure_protector_weights = self.find_treasure_protector_move_vectors(treasure_protector, weight_treasure_protector)

            aggregate_move_vectors = [
                (treasure_weights[i] + treasure_protector_weights[i]) * boundaries_weights[i] * move_vector
                for i, move_vector in enumerate(self._feasible_move_vectors)
            ]
        else:   
            aggregate_move_vectors = [
                (treasure_weights[i]) * boundaries_weights[i] * move_vector
                for i, move_vector in enumerate(self._feasible_move_vectors)
            ]

        aggregate_move_vectors_length = [
            np.linalg.norm(np.zeros((1, 2)) - move_vector)
            for move_vector in aggregate_move_vectors
        ]

        arg_max = max(range(len(aggregate_move_vectors_length)), key=aggregate_move_vectors_length.__getitem__)   
        next_move_vector = aggregate_move_vectors[arg_max if type(arg_max) is not list else arg_max[0]]
        
        # Deduct next move vector according to all vectors
        self.set_next_move_vector(next_move_vector)
        self.move()