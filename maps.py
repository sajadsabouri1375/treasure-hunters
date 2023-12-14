import json
import numpy as np


class Map:
    def __init__(self, **kwargs):
        self._map_name = kwargs.get('map_name', 'map_box_01')
        
        with open('assets/maps.json') as f:
            maps_configs = json.load(f)
        
        self._map_configs = maps_configs[self._map_name]
        self._aspect_ratio = (self._map_configs['aspect_ratio']['dx'], self._map_configs['aspect_ratio']['dy'])
        
        self._map_boundaries = []
        self.build_map()
        
    def get_boundaries(self):
        return self._map_boundaries
    
    def build_map(self):
        
        for block_name, block_address in self._map_configs['items']['blocks'].items():
            
            with open(f'assets/blocks/{block_address}.json') as f:
                block_properties = json.load(f)
                
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
            
