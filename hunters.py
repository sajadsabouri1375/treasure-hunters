from constrained_players import ConstrainedPlayer
from vector_utils import VectorUtils


class Hunter(ConstrainedPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._treasure_hunt_instruction = kwargs.get('treasure_hunt_instruction')
                
    def deduct_next_move(self, treasure_protector, treasure):
        
        # Deduct boundaries move vector using constrained player parent
        boundaries_move_vector = self.find_boundaries_move_vector()
        
        # Deduct treasure move vector and treasure protector move vector 
        '''
            Treasure guide vector and distance
        '''
        is_treasure_in_sight = True
        if is_treasure_in_sight:
            treasure_unit_vector = VectorUtils.find_unit_vector(treasure.get_current_position() - self.get_current_position())
            treasure_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure.get_current_position())
        
        '''
            Treasure protector guide vector and distance.
            Note that this matters only if treasure protector is in sight.
        '''
        is_treasure_protector_in_sight = VectorUtils.are_poits_in_sight(self.get_current_position(), treasure_protector.get_current_position(), self._map.get_boundaries())
        if is_treasure_protector_in_sight:
            treasure_protector_unit_vector = VectorUtils.find_unit_vector(-1 * (treasure_protector.get_current_position() - self.get_current_position()))
            treasure_protector_distance = VectorUtils.find_distance_between_two_points(self.get_current_position(), treasure_protector.get_current_position())
            treasure_protector_treasure_distance = VectorUtils.find_distance_between_two_points(treasure.get_current_position(), treasure_protector.get_current_position())

        if is_treasure_in_sight and is_treasure_protector_in_sight:
            td_to_tptd = treasure_distance / treasure_protector_treasure_distance
            
            treasure_vector_weight = self._treasure_hunt_instruction(td_to_tptd)

            next_move_vector = 10 * boundaries_move_vector + treasure_vector_weight * treasure_unit_vector + (1-treasure_vector_weight) * treasure_protector_unit_vector
        elif is_treasure_in_sight and not is_treasure_protector_in_sight:
            next_move_vector = 10 * boundaries_move_vector + 1 * treasure_unit_vector
        elif is_treasure_protector_in_sight and not is_treasure_in_sight:
            next_move_vector = 10 * boundaries_move_vector + 1 * treasure_protector_unit_vector
        else:
            next_move_vector = 10 * boundaries_move_vector
                
        # Deduct next move vector according to all vectors
        '''
            Finalize next move vector according to all calculations
            Note that this does NOT need to be a vector of length 1 (unit vector)
            bacause convertion to unit vector and inertia effect are considered in Player base class
        '''
        self.set_next_move_vector(next_move_vector)
        self.move()