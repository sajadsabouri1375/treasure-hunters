from matplotlib import pyplot as plt
from hunters import HunterState
from protectors import ProtectorState
from matplotlib.patches import Polygon
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
        for map_block in self._map.get_blocks():
            
            block_polygon = Polygon(map_block, hatch='.', fill=False, closed=True, linewidth=3, color='black', alpha=0.8)
            
            self._static_axes.add_patch(block_polygon)
    
        for map_container in self._map.get_containers():
            for vertex in map_container:
                
                start = vertex[0]
                finish = vertex[1]
                
                plt.plot(
                    [start[0,0], finish[0,0]],
                    [start[0,1], finish[0, 1]],
                    color='gray',
                    linewidth=3
                )
            
    def plot_mesh(self):
        vs = self._map._vertex_size
        
        for vertex in self._map._mesh:
            
            vertex_center = vertex.get_center()
            
            self._static_axes.scatter(
                vertex_center[0],
                vertex_center[1],
                color='magenta',
                alpha=0.4,
                s=0.5
            )
            
            if vertex._shortest_distance_to_treasure_vector is not None:  
                self._static_axes.arrow(
                    vertex_center[0],
                    vertex_center[1],
                    vertex._shortest_distance_to_treasure_vector[0]/3,
                    vertex._shortest_distance_to_treasure_vector[1]/3,
                    linewidth=0.5,
                    alpha=0.6
                )
            
            if vertex._shortest_distance_to_shelter_vector is not None:  
                self._static_axes.arrow(
                    vertex_center[0],
                    vertex_center[1],
                    vertex._shortest_distance_to_shelter_vector[0]/3,
                    vertex._shortest_distance_to_shelter_vector[1]/3,
                    linewidth=0.5,
                    color='red',
                    alpha=0.6
                )
            
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
                color='gray',
                linewidth=2,
                alpha=0.2
            )
        
    def plot_players(self):
        
        for player in self._hunters:

            if not player.is_active():
                continue

            player_state = player.get_hunter_state()
            positions = player.get_positions_history()
            
            for i in range(len(positions)-1, -1, -1):
                
                position = positions[i]
                scatter_size = 80 - ((len(positions) - i) * 70/len(positions))
                
                if i == len(positions) - 1:
                    new_element = self._dynamic_axes.scatter(
                        position[0,0],
                        position[0, 1],
                        color='blue' if player_state == HunterState.PLAYING else 'green',
                        s=scatter_size,
                        alpha=0.7,
                        edgecolors='b'
                    )
                    self._to_be_removes_elements.append(new_element)

                    new_element = self._dynamic_axes.text(
                        position[0, 0],
                        position[0, 1] + 0.01,
                        player.get_id(),
                        ha='center',
                        va='bottom',
                        fontsize='small'
                    )
                    self._to_be_removes_elements.append(new_element)

                else:
                    
                    if player_state == HunterState.PLAYING:
                        
                        new_element = self._dynamic_axes.scatter(
                            position[0,0],
                            position[0, 1],
                            color='blue',
                            s=scatter_size,
                            alpha=0.4
                        )
                        self._to_be_removes_elements.append(new_element)

            if player._protector_last_position_in_sight is not None and player._number_of_not_in_sight_escaping < player._number_of_maximum_not_in_sight_escaping and player._number_of_not_in_sight_escaping > 0:
                new_element = self._dynamic_axes.scatter(
                    player._protector_last_position_in_sight[0,0],
                    player._protector_last_position_in_sight[0, 1],
                    color='gray',
                    s=1000,
                    alpha=0.2,
                    edgecolors='gray'
                )
                self._to_be_removes_elements.append(new_element)
            
        for player in self._protectors:
            
            player_state = player.get_protector_state()
            positions = player.get_positions_history()
            
            for i in range(len(positions)-1, -1, -1):
                
                position = positions[i]
                scatter_size = 80 - ((len(positions) - i) * 70/len(positions))
                
                if i == len(positions) - 1:
                    new_element = self._dynamic_axes.scatter(
                        position[0,0],
                        position[0, 1],
                        color='red' if player_state == ProtectorState.PLAYING else 'green',
                        s=scatter_size,
                        alpha=0.7,
                        edgecolors='crimson'
                    )
                    self._to_be_removes_elements.append(new_element)

                    new_element = self._dynamic_axes.text(
                        position[0, 0],
                        position[0, 1] + 0.01,
                        player.get_id(),
                        ha='center',
                        va='bottom',
                        fontsize='small'
                    )
                    self._to_be_removes_elements.append(new_element)

                else:
                    
                    if player_state == ProtectorState.PLAYING:
                        
                        new_element = self._dynamic_axes.scatter(
                            position[0,0],
                            position[0, 1],
                            color='red',
                            s=scatter_size,
                            alpha=0.4
                        )
                        self._to_be_removes_elements.append(new_element)
            
    def plot_treasure(self):
        position = self._treasure.get_current_position()
        new_element = self._dynamic_axes.scatter(
            position[0,0], 
            position[0,1],
            color='gold',
            marker='v',
            alpha=0.8,
            s=600 if not self._treasure.get_is_hunted() else 200,
            edgecolors='coral'
        )
        self._to_be_removes_elements.append(new_element)

        if not self._treasure.get_is_hunted():
            new_element = plt.text(
                position[0,0],
                position[0,1]+0.015,
                'Treasure',
                va='bottom',
                ha='center',
                fontsize=10
            )
            self._to_be_removes_elements.append(new_element)

    def plot_shelter(self):
        position = self._shelter.get_position()
        self._static_axes.scatter(
            position[0,0], 
            position[0,1],
            color='cornflowerblue',
            marker='^',
            alpha=0.8,
            s=600,
            edgecolors='royalblue'
        )
    
        new_element = plt.text(
            position[0,0],
            position[0,1]-0.015,
            'Shelter',
            va='top',
            ha='center',
            fontsize=10
        )
            
    def remove_dynamic_elements(self):
        for element in self._to_be_removes_elements:
            element.remove()
        
        self._to_be_removes_elements = []

    def update_plot(self, fix):
             
        # Static elements
        if not self._are_statics_drawn:
            
            if self._instructions['plot_boundaries']:
                self.plot_boundaries()
            
            if self._instructions['plot_mesh']:
                self.plot_mesh()
            
            if self._instructions['plot_shelter']:
                self.plot_shelter()
                
            self._are_statics_drawn = True
        
        # Dynamic elements
        self.remove_dynamic_elements()

        if self._instructions['plot_players']:
            self.plot_players()
            
        if self._instructions['plot_treasure']: 
            self.plot_treasure()
                
        # Plot
        plt.tight_layout()
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()
        plt.gca().set_aspect('auto')
        
        if fix:
            plt.show(block=True)
