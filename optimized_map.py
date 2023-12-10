import numpy as np
from maps import Map
from graph_utils import Vertex
from copy import copy, deepcopy
import time
from multiprocessing import Pool
import sys
sys.setrecursionlimit(10000)

class OptimizedMap(Map):
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        
        self._point_of_interest = kwargs.get('point_of_interest')
        self._vertex_size = kwargs.get('vertex_size', 1)
        self._mesh = []
        self.create_mesh()
        
        min_distance_to_point_of_interest = np.inf
        for vertex in self._mesh:
            new_distance = np.linalg.norm(vertex.get_center() - self._point_of_interest)
            
            if new_distance < min_distance_to_point_of_interest:
                min_distance_to_point_of_interest = new_distance
                self._vertex_of_interest = vertex      
         
    def create_mesh(self):
        
        x_s = [boundary[0][0,0] for boundary in self.get_boundaries()]
        x_s.extend([boundary[1][0,0] for boundary in self.get_boundaries()])
        x_s = list(set(x_s))
        y_s = [boundary[0][0,1] for boundary in self.get_boundaries()]
        y_s.extend([boundary[1][0,1] for boundary in self.get_boundaries()])
        y_s = list(set(y_s))
        
        self._map_min_x = min(x_s)
        self._map_max_x = max(x_s)
        self._map_min_y = min(y_s)
        self._map_max_y = max(y_s)

        n_vertices_along_x = int((self._map_max_x - self._map_min_x) / self._vertex_size)
        n_vertices_along_y = int((self._map_max_y - self._map_min_y) / self._vertex_size)
        
        vertices_mean_along_x = np.linspace(self._map_min_x, self._map_max_x, n_vertices_along_x+1)[0:-1] + self._vertex_size / 2 
        vertices_mean_along_y = np.linspace(self._map_min_y, self._map_max_y, n_vertices_along_y+1)[0:-1] + self._vertex_size / 2
        
        # Initiate mesh
        for i in range(n_vertices_along_x):
            for j in range(n_vertices_along_y):
                self._mesh.append(
                    Vertex(
                        index=(i,j),
                        center=np.array([vertices_mean_along_x[i], vertices_mean_along_y[j]])
                    )
                )
                
        # Initiate mesh neighbors
        for vertex in self._mesh:
            vertex_index = vertex.get_index()
            
            for other_vertex in self._mesh:
                other_vertex_index = other_vertex.get_index()
                if (abs(other_vertex_index[0] - vertex_index[0]) == 1 and abs(other_vertex_index[1] - vertex_index[1]) == 0) or (abs(other_vertex_index[1] - vertex_index[1]) == 1 and abs(other_vertex_index[0] - vertex_index[0] == 0)) or (abs(other_vertex_index[0] - vertex_index[0]) == 1 and abs(other_vertex_index[1] - vertex_index[1]) == 1):
                    if other_vertex not in vertex.get_links():
                        vertex.add_links(other_vertex, np.linalg.norm(vertex.get_center() - other_vertex.get_center()))
                        other_vertex.add_links(vertex, np.linalg.norm(vertex.get_center() - other_vertex.get_center()))
    
    def find_min_route_between_vertices(self, args):
        
        vertex_i, vertex_j, traversed_vertices = args
        
        traversed_vertices.append(vertex_i)
        
        if vertex_i == vertex_j:
            return 0, None
        
        if vertex_i._shortest_distance != np.inf:
            return vertex_i._shortest_distance, None
        
        min_distance = np.inf
        min_distance_vector = None
        
        for linked_vertex, linked_vertex_distance in zip(vertex_i.get_links(), vertex_i.get_distances()):
            
            if linked_vertex not in traversed_vertices:  
                
                distance, _ = self.find_min_route_between_vertices(
                    (
                        linked_vertex, 
                        vertex_j,
                        copy(traversed_vertices)
                    )
                )
                distance = linked_vertex_distance + distance
                
                if distance < min_distance:
                    min_distance = distance
                    min_distance_vector = linked_vertex
        
        if min_distance < vertex_i._shortest_distance:
            vertex_i._shortest_distance = min_distance
            vertex_i._shortest_distance_vector = min_distance_vector
        
        return min_distance, min_distance_vector
    
    def optimize_routes(self):
        for vertex in self._mesh:
            vertex._shortest_distance, vertex._shortest_distance_vector = self.find_min_route_between_vertices(
                (vertex, self._vertex_of_interest, [])
            )
    
if __name__ == "__main__":
    start_time = time.time()
    map = OptimizedMap(
        map_name='map_box_01',
        point_of_interest=np.array([0.9, 0.9]),
        vertex_size = 0.03
    )
    
    map.optimize_routes()
    
    finish_time = time.time()
    
    print(finish_time - start_time)
    
    print('done')
    