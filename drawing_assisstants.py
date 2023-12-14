from matplotlib import pyplot as plt
import matplotlib
plt.ion()

class DrawingAssisstant:
    def __init__(self, **kwargs):
        
        self._instructions = kwargs.get('instructions', {'plot_mesh': False, 'plot_boundaries': True, 'plot_players': True, 'plot_treasure': True})
        plt.ion()
        self._figure = plt.figure(figsize=(25.6, 14.4))
        self._static_axes = plt.gca()
        self._dynamic_axes = plt.gca()
        self._map = kwargs.get('map', None)
        self._hunters = kwargs.get('hunters')
        self._protectors = kwargs.get('protectors')
        self._treasure = kwargs.get('treasure')
        self._to_be_removes_elements = []
        self._are_statics_drawn = False
        
    def plot_boundaries(self):
        for boundary in self._map.get_boundaries():
            point_01 = boundary[0]
            point_02 = boundary[1]
            
            self._static_axes.plot(
                [point_01[0,0], point_02[0,0]],
                [point_01[0,1], point_02[0,1]],
                color='black',
                alpha=0.7,
                linewidth=4
            )
    
    def plot_mesh(self):
        vs = self._map._vertex_size
        
        for vertex in self._map._mesh:
            
            vertex_center = vertex.get_center()
            
            self._static_axes.scatter(
                vertex_center[0],
                vertex_center[1],
                color='magenta',
                alpha=0.5,
                s=0.5
            )
            
            if vertex._shortest_distance_vector is not None:  
                self._static_axes.arrow(vertex_center[0], vertex_center[1], vertex._shortest_distance_vector[0]/2, vertex._shortest_distance_vector[1]/2, linewidth=0.5)
            
            self._static_axes.plot(
                [
                    vertex_center[0] - vs/2,
                    vertex_center[0] - vs/2,
                    vertex_center[0] + vs/2,
                    vertex_center[0] + vs/2,
                    vertex_center[0] - vs/2
                ],
                [
                    vertex_center[1] - vs/2,
                    vertex_center[1] + vs/2,
                    vertex_center[1] + vs/2,
                    vertex_center[1] - vs/2,
                    vertex_center[1] - vs/2
                ],
                color='black',
                linewidth=0.5
            )
        
    def plot_players(self):
        for player in self._hunters:
            position = player.get_current_position()
            new_element = self._dynamic_axes.scatter(
                position[0,0],
                position[0, 1],
                color='blue',
                s=15,
                alpha=0.9
            )
            self._to_be_removes_elements.append(new_element)
            
            previous_position = player.get_previous_position()
            new_element = self._dynamic_axes.scatter(
                previous_position[0,0],
                previous_position[0, 1],
                color='blue',
                s=5,
                alpha=0.4
            )
            self._to_be_removes_elements.append(new_element)

        for player in self._protectors:
            position = player.get_current_position()
            new_element = self._dynamic_axes.scatter(
                position[0,0],
                position[0, 1],
                color='red',
                s=15,
                alpha=0.9
            )
            self._to_be_removes_elements.append(new_element)

            previous_position = player.get_previous_position()
            new_element = self._dynamic_axes.scatter(
                previous_position[0,0],
                previous_position[0, 1],
                color='red',
                s=5,
                alpha=0.4
            )
            self._to_be_removes_elements.append(new_element)

    def plot_treasure(self):
        position = self._treasure.get_current_position()
        self._static_axes.scatter(
            position[0,0], 
            position[0,1],
            color='magenta',
            linewidth=4,
            alpha=0.8
        )
    
    def remove_dynamic_elements(self):
        for element in self._to_be_removes_elements:
            element.remove()
        
        self._to_be_removes_elements = []

    def update_plot(self):
             
        # Static elements
        if not self._are_statics_drawn:
            
            if self._instructions['plot_boundaries']:
                self.plot_boundaries()
            
            if self._instructions['plot_mesh']:
                self.plot_mesh()
            
            if self._instructions['plot_treasure']: 
                self.plot_treasure()
            
            self._are_statics_drawn = True
        
        # Dynamic elements
        if self._instructions['plot_players']:
            self.remove_dynamic_elements()
            self.plot_players()
        
        # Plot
        plt.tight_layout()
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()
        plt.gca().set_aspect('auto')
