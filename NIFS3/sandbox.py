import cv2
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from matplotlib.backend_bases import MouseButton
import os
import subprocess

fig = plt.figure()
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')

class NIFS3:
    def get_nifs3(points):
        x = []
        y = []

        p = subprocess.Popen(["calc_nifs3.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        p.stdin.write(f"{len(points)}\n".encode("utf-8"))
        for tx, ty in points:
            p.stdin.write(f"{tx} {ty}\n".encode("utf-8"))
            p.stdin.flush()

        while True:
            line = p.stdout.readline()
            if not line:
                break

            a, b = line.rstrip().decode("utf-8").split()
            x.append(float(a))
            y.append(float(b))

        return x, y


class GUI:
    def __init__(self, image_path):
        self.coordinates = [[]]
        self.done = False
        self.mark_dots = True
        self.draw = True

        plt.cla()
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        plt.imshow(self.image, cmap='gray', vmin=0, vmax=255)

        fig.canvas.callbacks.connect('button_press_event', self.on_click)
        fig.canvas.callbacks.connect('key_press_event', self.on_press)

        print("Left-click to add point, right-click to remove point\n"+
              "Enter to separate point groups, backspace to remove last group\n"+
              "m to enable/disable marking dots\n"+
              "d to enable/disable drawing\n"+
              "Escape to end")
    
    def on_click(self, event):
        if self.draw:
            if(event.button is MouseButton.LEFT):
                self.coordinates[len(self.coordinates)-1].append((event.xdata, event.ydata))
            elif(event.button is MouseButton.RIGHT and len(self.coordinates[len(self.coordinates)-1]) > 0):
                self.coordinates[len(self.coordinates)-1].pop()
            self.update_view()
    
    def on_press(self, event):
        if(event.key == 'enter'): self.coordinates.append([])
        elif(event.key == 'backspace'):
            if(self.coordinates[len(self.coordinates)-1] != []):
                self.coordinates[len(self.coordinates)-1] = []
            elif(len(self.coordinates) > 1):
                self.coordinates.pop() 
        elif(event.key == 'escape'): self.done = True
        elif(event.key == 'm'): self.mark_dots = not self.mark_dots
        elif(event.key == 'd'): self.draw = not self.draw
        self.update_view()

    def update_view(self):
        plt.cla()
        plt.imshow(self.image, cmap='gray', vmin=0, vmax=255)
        
        for c in self.coordinates:
            if(len(c) > 2):
                x, y = NIFS3.get_nifs3(c)
                if self.mark_dots: plt.scatter(*zip(*c), color = "red")
                ax.plot(x, y, '-')
            else:
                if self.mark_dots and len(c) > 0:
                    ax.scatter(*zip(*c), color = "red")
                ax.plot(*zip(*c), '-')
        plt.show(block=False)

    def start(self):
        while not self.done:
            plt.pause(0.001)
        return self.coordinates

gui = GUI("text.png")
res = gui.start()

for file in os.listdir("./points"):
    if file.endswith(".in"):
        os.remove(f"points/{file}")

for (i, coordinates) in enumerate(res):
    with open(f"./points/points{i}.in", "w") as file:
        file.write(f"{len(coordinates)}\n")
        for(x, y) in coordinates:
            file.write(f"{x} {-y}\n")
