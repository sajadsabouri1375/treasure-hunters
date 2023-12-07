from matplotlib import pyplot as plt
import matplotlib
plt.ion()

class DrawingAssisstant:
    def __init__(self, **kwargs):
        self._figure = plt.figure(figsize=(25.6, 14.4))
        self._map = kwargs.get('map', None)
        self._hunters = kwargs.get('hunters')
        self._protectors = kwargs.get('protectors')
        self._treasure = kwargs.get('treasure')

    def plot_boundaries(self):
        for boundary in self._map.get_boundaries():
            point_01 = boundary[0]
            point_02 = boundary[1]
            
            plt.gca().plot(
                [point_01[0,0], point_02[0,0]],
                [point_01[0,1], point_02[0,1]],
                color='black',
                alpha=0.7,
                linewidth=4
            )
    
    def plot_players(self):
        for player in self._hunters:
            position = player.get_current_position()
            plt.gca().scatter(
                position[0,0],
                position[0, 1],
                color='blue',
                linewidth=2,
                alpha=0.9
            )
        for player in self._protectors:
            position = player.get_current_position()
            plt.gca().scatter(
                position[0,0],
                position[0, 1],
                color='red',
                linewidth=2,
                alpha=0.9
            )
            
    def plot_treasure(self):
        position = self._treasure.get_current_position()
        plt.gca().scatter(
            position[0,0], 
            position[0,1],
            color='magenta',
            linewidth=4,
            alpha=0.8
        )
        
    def update_plot(self):
        plt.cla()
        self.plot_boundaries()
        self.plot_players()
        self.plot_treasure()
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()
