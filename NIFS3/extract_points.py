import cv2
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from matplotlib.backend_bases import MouseButton
import os

fig = plt.figure()
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')

class Extractor:
    def __init__(self, image_path):
        self.coordinates = [[]]
        self.done = False

        plt.cla()
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        plt.imshow(self.image, cmap='gray', vmin=0, vmax=255)

        fig.canvas.callbacks.connect('button_press_event', self.on_click)
        fig.canvas.callbacks.connect('key_press_event', self.on_press)

        print("Left-click to add point, right-click to remove point\n"+
              "Enter to separate point groups, backspace to remove last group\n"+
              "Escape to end")

    
    def on_click(self, event):
        if(event.button is MouseButton.LEFT):
            self.coordinates[len(self.coordinates)-1].append((event.xdata, event.ydata))
        elif(event.button is MouseButton.RIGHT and len(self.coordinates[len(self.coordinates)-1]) > 0):
            self.coordinates[len(self.coordinates)-1].pop()
    
    def on_press(self, event):
        if(event.key == 'enter'): self.coordinates.append([])
        elif(event.key == 'backspace' and len(self.coordinates) > 1): self.coordinates.pop() 
        elif(event.key == 'escape'): self.done = True
        print(self.coordinates[len(self.coordinates)-1])

    def update_view(self):
        plt.cla()
        plt.imshow(self.image, cmap='gray', vmin=0, vmax=255)
        
        for c in self.coordinates:
            ax.plot(*zip(*c), 'o-')
        plt.show(block=False)


    def extract_coordinates(self):        # diaply image and let user pick points and separate them with enter
        while not self.done:
            self.update_view()
            plt.pause(0.01)

        return self.coordinates

e = Extractor("text.png")

for file in os.listdir("./points"):
    if file.endswith(".in"):
        os.remove(f"points/{file}")

for (i, coordinates) in enumerate(e.extract_coordinates()):
    with open(f"./points/points{i}.in", "w") as file:
        file.write(f"{len(coordinates)}\n")
        for(x, y) in coordinates:
            file.write(f"{x} {-y}\n")
