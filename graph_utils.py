import numpy as np


class Vertex:
    def __init__(self, **kwargs):
        self._index = kwargs.get('index')
        self._center = kwargs.get('center')
        
        # Initiate default values for a new vertex
        self._linked_vertices = []
        self._linked_vertices_distances = []
        self._shortest_distance_to_treasure = np.inf
        self._shortest_distance_to_treasure_vector = None
        self._shortest_distance_to_shelter = np.inf
        self._shortest_distance_to_shelter_vector = None
        
    def get_center(self):
        return self._center
    
    def get_index(self):
        return self._index
    
    def get_links(self):
        return self._linked_vertices
    
    def get_distances(self):
        return self._linked_vertices_distances
    
    def add_links(self, new_vertex, distance):
        self._linked_vertices.append(new_vertex)
        self._linked_vertices_distances.append(distance)
    
    