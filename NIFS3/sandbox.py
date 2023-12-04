import cv2
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from matplotlib.backend_bases import MouseButton
import os
import subprocess

"""
cpp script is faster (and better tested), but requires calc_nifs3.cpp to be compiled to calc_nifs3.exe
python is python
"""
USE_CPP = False

fig = plt.figure()
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')

class NIFS3:
    def __init__(self):
        self.x0 = []
        self.y0 = []
        self.n = 0
        self.t = []
        self.Mx = []
        self.My = []

    def get_nifs3(self, points):
        if USE_CPP:
            return self.calc_nifs3_cpp(points)
        else:
            return self.calc_nifs3_py(points)
    
    def calc_nifs3_cpp(self, points):
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
    
    def calc_nifs3_py(self, points):
        self.x0 = []
        self.y0 = []
        for x, y in points:
            self.x0.append(x)
            self.y0.append(y)
        
        self.nifs3_update()

        res_x = []
        res_y = []
        T = self.t[0]
        while T <= self.t[len(self.t)-1]:
            res_x.append(self.calc_nifs3(T, self.x0, self.Mx))
            res_y.append(self.calc_nifs3(T, self.y0, self.My))
            T += 0.001

        return res_x, res_y

    def nifs3_update(self):
        self.n = len(self.x0)-1
        
        self.t = []
        for i in range(len(self.x0)):
            self.t.append(i/self.n)

        self.Mx = self.calc_M(self.x0)
        self.My = self.calc_M(self.y0)
    
    def calc_M(self, x):
        q = [0]
        p = [0]
        u = [0]

        k = 1
        while k <= self.n-1:
            lk = self.calc_lam(k)
            p.append(lk * q[k-1] + 2)
            q.append((lk-1)/p[k])
            u.append((self.dk(k, x) - lk * u[k-1])/p[k])
            k += 1
        
        M = [0] * (self.n+1)
        M[self.n] = 0
        M[self.n-1] = u[self.n-1]
        k = self.n-2
        while k >= 0:
            M[k] = u[k] - q[k] * M[k+1]
            k -= 1
        
        return M
    
    def calc_lam(self, k):
        return (self.t[k] - self.t[k-1])/(self.t[k+1] - self.t[k-1])
    
    def dk(self, k, x):
        t1 = (x[k+1] - x[k])/(self.t[k+1] - self.t[k])
        t2 = (x[k] - x[k-1])/(self.t[k] - self.t[k-1])
        return 6 * (t1 - t2)/(self.t[k+1] - self.t[k-1])
    
    def calc_nifs3(self, X, x0, M):
        k = 1
        while self.t[k] < X: k += 1

        return (1/(self.t[k]-self.t[k-1])) \
            * (M[k-1]*pow(self.t[k] - X, 3)/6.
            +  M[k] * pow(X - self.t[k-1], 3)/6. 
            + (x0[k-1] - M[k-1]*pow(self.t[k]-self.t[k-1], 2)/6.)*(self.t[k]-X)
            + (x0[k] - M[k]*pow(self.t[k]-self.t[k-1], 2)/6.)*(X-self.t[k-1]));


class GUI:
    def __init__(self, image_path):
        self.coordinates = [[]]
        self.done = False
        self.mark_dots = True
        self.draw = True
        self.nifs3 = NIFS3()

        plt.cla()
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        plt.imshow(self.image, cmap='gray', vmin=0, vmax=255)

        fig.canvas.callbacks.connect('button_press_event', self.on_click)
        fig.canvas.callbacks.connect('key_press_event', self.on_press)

        print("Left-click to add point, right-click to remove point\n"+
              "Enter to separate point groups, backspace to remove last group\n"+
              "m to enable/disable marking points\n"+
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
                x, y = self.nifs3.get_nifs3(c)
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
            if not plt.fignum_exists(1):
                self.done = True
        return self.coordinates

gui = GUI("text.png")
res = gui.start()

if not os.path.exists("./points"):
    os.makedirs("./points")
for file in os.listdir("./points"):
    if file.endswith(".in"):
        os.remove(f"points/{file}")

for (i, coordinates) in enumerate(res):
    with open(f"./points/points{i}.in", "w") as file:
        file.write(f"{len(coordinates)}\n")
        for(x, y) in coordinates:
            file.write(f"{x} {-y}\n")
