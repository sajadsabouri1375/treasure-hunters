from matplotlib import pyplot as plt
import matplotlib
plt.ion()

class DrawingAssisstant:
    def __init__(self, **kwargs):
        
        plt.ion()

        self._instructions = kwargs.get('instructions', {'plot_mesh': False, 'plot_boundaries': True, 'plot_players': True, 'plot_treasure': True, 'plot_shelter': True})
        self._map = kwargs.get('map', None)
        self._hunters = kwargs.get('hunters')
        self._protectors = kwargs.get('protectors')
        self._treasure = kwargs.get('treasure')
        self._shelter = kwargs.get('shelter')

        # Initialize new drawing assisstant with default values (The screen is supposed to be 2K)
        self._figure = plt.figure(figsize=(25.6, 14.4))
        self._static_axes = plt.gca()
        self._dynamic_axes = plt.gca()
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
            
            if vertex._shortest_distance_to_treasure_vector is not None:  
                self._static_axes.arrow(vertex_center[0], vertex_center[1], vertex._shortest_distance_to_treasure_vector[0]/3, vertex._shortest_distance_to_treasure_vector[1]/3, linewidth=0.5)
            
            if vertex._shortest_distance_to_shelter_vector is not None:  
                self._static_axes.arrow(vertex_center[0], vertex_center[1], vertex._shortest_distance_to_shelter_vector[0]/3, vertex._shortest_distance_to_shelter_vector[1]/3, linewidth=0.5, color='red')
            
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
                s=40,
                alpha=0.9
            )
            self._to_be_removes_elements.append(new_element)
            
            previous_position = player.get_previous_position()
            new_element = self._dynamic_axes.scatter(
                previous_position[0,0],
                previous_position[0, 1],
                color='blue',
                s=15,
                alpha=0.4
            )
            self._to_be_removes_elements.append(new_element)

            if player._protector_last_position_in_sight is not None and player._number_of_not_in_sight_escaping < player._number_of_maximum_not_in_sight_escaping and player._number_of_not_in_sight_escaping > 0:
                new_element = self._dynamic_axes.scatter(
                    player._protector_last_position_in_sight[0,0],
                    player._protector_last_position_in_sight[0, 1],
                    color='gray',
                    s=100,
                    alpha=0.2
                )
                self._to_be_removes_elements.append(new_element)
            
        for player in self._protectors:
            position = player.get_current_position()
            new_element = self._dynamic_axes.scatter(
                position[0,0],
                position[0, 1],
                color='red',
                s=40,
                alpha=0.9
            )
            self._to_be_removes_elements.append(new_element)

            previous_position = player.get_previous_position()
            new_element = self._dynamic_axes.scatter(
                previous_position[0,0],
                previous_position[0, 1],
                color='red',
                s=12,
                alpha=0.4
            )
            self._to_be_removes_elements.append(new_element)

    def plot_treasure(self):
        position = self._treasure.get_current_position()
        self._static_axes.scatter(
            position[0,0], 
            position[0,1],
            color='magenta',
            marker='1',
            alpha=0.8,
            s=400
        )
    
    def plot_shelter(self):
        position = self._shelter.get_position()
        self._static_axes.scatter(
            position[0,0], 
            position[0,1],
            color='blue',
            marker='2',
            alpha=0.8,
            s=400
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
            
            if self._instructions['plot_shelter']:
                self.plot_shelter()
                
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
