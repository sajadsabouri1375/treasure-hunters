import numpy as np


class Vertex:
    def __init__(self, **kwargs):
        self._index = kwargs.get('index')
        self._center = kwargs.get('center')
        self._linked_vertices = []
        self._linked_vertices_distances = []
        self._shortest_distance = np.inf
        self._shortest_distance_vector = None
        
    def get_center(self):
        return self._center
    
    def get_index(self):
        return self._index
    
    def add_links(self, new_vertex, distance):
        self._linked_vertices.append(new_vertex)
        self._linked_vertices_distances.append(distance)
    
    def get_links(self):
        return self._linked_vertices
    
    def get_distances(self):
        return self._linked_vertices_distances
    
    