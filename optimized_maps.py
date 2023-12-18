import numpy as np
from maps import Map
from graph_utils import Vertex
from copy import copy, deepcopy
import time
from multiprocessing import Pool
from vector_utils import VectorUtils
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import sys
sys.setrecursionlimit(10000)


class OptimizedMap(Map):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._treasure = kwargs.get('treasure')
        self._shelter = kwargs.get('shelter')
        self._vertex_size = kwargs.get('vertex_size', 1)
        
        self._mesh:list(Vertex) = []
        self.create_mesh()
        
        # Deduct treasure and shelter vertices according to mesh
        self._shelter_vertex_of_interest = self.find_vertex_of_interest(self._shelter)
        self._treasure_vertex_of_interest = self.find_vertex_of_interest(self._treasure)

    def find_vertex_of_interest(self, point_of_interest):
        
        min_distance_to_point_of_interest = np.inf
        
        for vertex in self._mesh:
            new_distance = np.linalg.norm(vertex.get_center() - point_of_interest)
            
            if new_distance < min_distance_to_point_of_interest:
                min_distance_to_point_of_interest = new_distance
                vertex_of_interest = vertex      
        
        return vertex_of_interest
    
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
                new_point = Point(vertices_mean_along_x[i], vertices_mean_along_y[j])
                
                if not self.is_point_inside_blocks(new_point):
                    center = np.array([vertices_mean_along_x[i], vertices_mean_along_y[j]])
                    new_vertex = Vertex(
                        index=(i,j),
                        center=center
                    )
                    self._mesh.append(
                        new_vertex
                    )
                
        # Initiate mesh neighbors
        for vertex in self._mesh:
            vertex_index = vertex.get_index()
            
            for other_vertex in self._mesh:
                other_vertex_index = other_vertex.get_index()
                if  (abs(other_vertex_index[0] - vertex_index[0]) == 1 and abs(other_vertex_index[1] - vertex_index[1]) == 0) or \
                    (abs(other_vertex_index[1] - vertex_index[1]) == 1 and abs(other_vertex_index[0] - vertex_index[0] == 0)) or \
                    (abs(other_vertex_index[0] - vertex_index[0]) == 1 and abs(other_vertex_index[1] - vertex_index[1]) == 1):
                        
                    if other_vertex not in vertex.get_links():
                        
                        does_hit_the_boundaries = False
                        for boundary in self.get_boundaries():
                            
                            intersection = VectorUtils.find_part_lines_intersection(
                                boundary,
                                [
                                    vertex.get_center(),
                                    other_vertex.get_center()
                                ]
                            )
                            
                            if intersection is None:
                                continue
                            else:
                                does_hit_the_boundaries = True
                        
                        if not does_hit_the_boundaries:
                            vertices_distance = np.linalg.norm(vertex.get_center() - other_vertex.get_center())
                            vertex.add_links(other_vertex, vertices_distance)
                            other_vertex.add_links(vertex, vertices_distance)
    
        self._vertices_centers = []
        for vertex in self._mesh:
            self._vertices_centers.append(vertex.get_center())
            
        self._vertices_centers = np.array(self._vertices_centers)
        
    def find_min_route_between_vertices(self, vertex_i, vertex_j, traversed_vertices=[], mode='treasure'):
                
        traversed_vertices.append(vertex_i)
        
        if mode == 'treasure':
            if vertex_i._shortest_distance_to_treasure != np.inf and vertex_i._shortest_distance_to_treasure_vector is not None:
                return vertex_i._shortest_distance_to_treasure, vertex_i._shortest_distance_to_treasure_vector

        elif mode == 'shelter':
            if vertex_i._shortest_distance_to_shelter != np.inf and vertex_i._shortest_distance_to_shelter_vector is not None:
                return vertex_i._shortest_distance_to_shelter, vertex_i._shortest_distance_to_shelter_vector
            
        if vertex_i == vertex_j:
            return 0, None
        
        min_distance = np.inf
        min_distance_vector = None
        
        for linked_vertex, linked_vertex_distance in zip(vertex_i.get_links(), vertex_i.get_distances()):
            
            if linked_vertex not in traversed_vertices:  
                
                distance, _ = self.find_min_route_between_vertices(
                    linked_vertex, 
                    vertex_j,
                    copy(traversed_vertices),
                    mode
                )
                distance = linked_vertex_distance + distance
                
                if distance < min_distance:
                    min_distance = distance
                    min_distance_vector = copy(linked_vertex)
        
        if mode == 'treasure':
            if min_distance < vertex_i._shortest_distance_to_treasure:
                vertex_i._shortest_distance_to_treasure = min_distance
                vertex_i._shortest_distance_to_treasure_vector = min_distance_vector.get_center() - vertex_i.get_center()
                
        elif mode == 'shelter':
            if min_distance < vertex_i._shortest_distance_to_shelter:
                vertex_i._shortest_distance_to_shelter = min_distance
                vertex_i._shortest_distance_to_shelter_vector = min_distance_vector.get_center() - vertex_i.get_center()
        
        if mode == 'treasure':
            return vertex_i._shortest_distance_to_treasure, vertex_i._shortest_distance_to_treasure_vector
        elif mode == 'shelter':
            return vertex_i._shortest_distance_to_shelter, vertex_i._shortest_distance_to_shelter_vector

    def optimize_routes(self):
        
        # Optimize routes for treasure
        for vertex in self._mesh:
            vertex._shortest_distance_to_treasure, vertex._shortest_distance_to_treasure_vector = self.find_min_route_between_vertices(
                vertex, self._treasure_vertex_of_interest, [], 'treasure'
            )
            
        # Optimize routes for shelter
        for vertex in self._mesh:
            vertex._shortest_distance_to_shelter, vertex._shortest_distance_to_shelter_vector = self.find_min_route_between_vertices(
                vertex, self._shelter_vertex_of_interest, [], 'shelter'
            )
            
    def return_vertex_including_position(self, position):
    
        distances = np.sum(np.square(self._vertices_centers - position), axis=1)
        return self._mesh[distances.argmin()]
    
    def get_distance_and_move_vector(self, position, mode='treasure'):
        
        inclusive_vertex = self.return_vertex_including_position(position)
        
        if mode == 'treasure':
            return inclusive_vertex._shortest_distance_to_treasure, inclusive_vertex._shortest_distance_to_treasure_vector
        elif mode == 'shelter':
            return inclusive_vertex._shortest_distance_to_shelter, inclusive_vertex._shortest_distance_to_shelter_vector
        
if __name__ == "__main__":
    start_time = time.time()
    map = OptimizedMap(
        map_name='map_01',
        point_of_interest=np.array([0.9, 0.9]).reshape(1, -1),
        vertex_size = 0.07
    )
    
    map.optimize_routes()
    
    finish_time = time.time()
    
    print(finish_time - start_time)
    
    print('done')
    