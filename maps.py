import json
import numpy as np
from shapely.geometry.polygon import Polygon


class Map:
    def __init__(self, **kwargs):
        self._map_name = kwargs.get('map_name', 'map_box_01')
        
        with open('assets/maps.json') as f:
            maps_configs = json.load(f)
        
        self._map_configs = maps_configs[self._map_name]
        self._aspect_ratio = (self._map_configs['aspect_ratio']['dx'], self._map_configs['aspect_ratio']['dy'])
        self._map_blocks = []
        self._map_blocks_polygons = []
        self._map_containers = []
        self._map_containers_polygons = []
        self._map_boundaries = []
        self.build_map()
        
    def get_boundaries(self):
        return self._map_boundaries
    
    def get_blocks(self):
        return self._map_blocks
    
    def get_containers(self):
        return self._map_containers
    
    def get_block_polygons(self):
        return self._map_blocks_polygons
    
    def get_containers_polygons(self):
        return self._map_containers_polygons
    
    def build_map(self):
        
        for block_name, block_address in self._map_configs['items']['blocks'].items():
            
            with open(f'assets/blocks/{block_address}.json') as f:
                block_properties = json.load(f)
            
            current_block = []
            for line, line_properties in block_properties.items():
                point_start = np.array(
                    [
                        line_properties['start']['x'],
                        line_properties['start']['y']
                    ]
                ).reshape(1, -1)
                point_end = np.array(
                    [
                        line_properties['end']['x'],
                        line_properties['end']['y']
                    ]
                ).reshape(1, -1)
            
                self._map_boundaries.append([point_start, point_end])
                
                current_block.append(
                    (line_properties['start']['x'], line_properties['start']['y'])
                )
                current_block.append(
                    (line_properties['end']['x'], line_properties['end']['y'])
                )
                
            self._map_blocks.append(current_block)
        
        self.build_blocks_polygons()
        
        for container_name, container_address in self._map_configs['items']['containers'].items():
            
            with open(f'assets/containers/{container_address}.json') as f:
                container_properties = json.load(f)
            
            current_container = []
            for line, line_properties in container_properties.items():
                point_start = np.array(
                    [
                        line_properties['start']['x'],
                        line_properties['start']['y']
                    ]
                ).reshape(1, -1)
                point_end = np.array(
                    [
                        line_properties['end']['x'],
                        line_properties['end']['y']
                    ]
                ).reshape(1, -1)
            
                self._map_boundaries.append([point_start, point_end])
                current_container.append([point_start, point_end])
            
            self._map_containers.append(current_container)
            
    def build_blocks_polygons(self):
        for block in self._map_blocks:
            self._map_blocks_polygons.append(
                Polygon(
                    block
                )
            )
            
    def is_point_inside_blocks(self, point):
        for polygon in self._map_blocks_polygons:
            if polygon.contains(point):
                return True
            
        return False