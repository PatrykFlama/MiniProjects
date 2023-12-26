import cv2
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from matplotlib.backend_bases import MouseButton
import os
import subprocess

resolution = 0.001

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

    def get_nifs3(self, points, points_per_segment):
        self.x0 = []
        self.y0 = []
        for x, y in points:
            self.x0.append(x)
            self.y0.append(y)
        
        self.nifs3_update()

        res_x = []
        res_y = []        
        for segment in range(0, len(points)-1):     # walk thru segments
            Tfrom = self.t[segment]
            Tto = self.t[segment+1]
            for k in range(points_per_segment[segment]): # walk thru points in segment, with given resolution   
                T = Tfrom + k * (Tto - Tfrom) / (points_per_segment[segment]-1)
                res_x.append(self.calc_nifs3(T, self.x0, self.Mx))
                res_y.append(self.calc_nifs3(T, self.y0, self.My))

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
            M[k] = u[k] + q[k] * M[k+1]
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
        self.points_per_segment = 2
        self.resolution = [[]]
        self.nifs3 = NIFS3()
        self.done = False
        self.mark_dots = True
        self.draw = True
        self.display_image = True

        plt.cla()
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        self.update_view()

        fig.canvas.callbacks.connect('button_press_event', self.on_click)
        fig.canvas.callbacks.connect('key_press_event', self.on_press)

        print("Left-click to add point, right-click to remove point\n"+
              "Enter to separate point groups, backspace to remove last group\n"+
              "m to enable/disable marking points\n"+
              "d to enable/disable drawing\n"+
              "i to enable/disable image background\n"+
              "Escape to end")
    
    def on_click(self, event):
        if self.draw:
            if(event.button is MouseButton.LEFT and event.xdata is not None and event.ydata is not None):
                self.coordinates[len(self.coordinates)-1].append((event.xdata, event.ydata))
                self.resolution[len(self.resolution)-1].append(self.points_per_segment)
            elif(event.button is MouseButton.RIGHT and len(self.coordinates[len(self.coordinates)-1]) > 0):
                self.coordinates[len(self.coordinates)-1].pop()
                self.resolution[len(self.resolution)-1].pop()
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
        elif(event.key == 'i'): self.display_image = not self.display_image
        elif(event.key == '8'): self.points_per_segment += 10
        elif(event.key == '/'): self.points_per_segment -= 10
        elif(event.key == '='): self.points_per_segment += 1
        elif(event.key == '-'): self.points_per_segment -= 1
        
        self.points_per_segment = max(2, self.points_per_segment)
        if len(self.resolution[len(self.resolution)-1]) > 1:
            self.resolution[len(self.resolution)-1][-2] = self.points_per_segment
        self.update_view()

    def update_view(self):
        plt.cla()

        plt.title(f"Editing function {len(self.coordinates)}")

        if self.display_image:
            plt.imshow(self.image, cmap='gray', vmin=0, vmax=255)
        else:
            plt.imshow(self.image, cmap='gray', vmin=0, vmax=1)

        for c, r in zip(self.coordinates, self.resolution):
            if(len(c) > 2):
                x, y = self.nifs3.get_nifs3(c, r)
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
        return self.coordinates, self.resolution




print("1 for interactive editing mode\n2 to display points from file")
choice = input()

if choice[0] == "1":
    if not os.path.exists("./text.png"):
        print("Background image ./text.png not found!")
        exit()

    gui = GUI("text.png")
    res, resolution = gui.start()

    if not os.path.exists("./points"):
        os.makedirs("./points")

    for (i, coordinates) in enumerate(res):
        if len(coordinates) == 0: continue

        if os.path.exists(f"./points/points{i}.txt"):
            os.remove(f"./points/points{i}.txt")

        with open(f"./points/points{i}.txt", "w") as file:
            cnt = 0
            for (x, y), r in zip(coordinates, resolution[i]):
                t = cnt / (len(coordinates)-1)
                file.write(f"{t} {x} {-y} {r}\n")
    for i in range(len(res), 100):
        if os.path.exists(f"./points/points{i}.txt"):
            os.remove(f"./points/points{i}.txt")

elif choice[0] == "2":
    if not os.path.exists("./points"):
        print("No points found")
        exit()

    print("press i for image background, m for marking input points\n")

    nifs3 = NIFS3()
    x = []
    y = []
    coordinates = []
    resolution = []
    for file in os.listdir("./points"):
        if file.endswith(".txt"):
            tab = ([(float(x), -float(y), int(r)) for (t, x, y, r) in [line.rstrip().split() for line in open(f"./points/{file}", "r")]])
            c = [(x, y) for x, y, r in tab]
            r = [r for x, y, r in tab]
            coordinates.append(c)
            resolution.append(r)
            tx, ty = nifs3.get_nifs3(c, r)
            x.append(tx)
            y.append(ty)

    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')

    display_image = True
    mark_dots = False
    done = False
    image = None
    try: 
        image = cv2.imread("./text.png", cv2.IMREAD_GRAYSCALE)
    except:
        pass

    def update_view():
        global display_image, mark_dots
        plt.cla()

        if display_image and image is not None:
            plt.imshow(image, cmap='gray', vmin=0, vmax=255)
        else:
            plt.imshow(image, cmap='gray', vmin=0, vmax=1)
        
        if mark_dots: 
            for c in coordinates:
                plt.scatter(*zip(*c), color = "red")

        for tx, ty in zip(x, y):
            plt.plot(tx, ty)

        plt.show(block=False)

    def on_press(event):
        global display_image, mark_dots
        if(event.key == 'i'): display_image = not display_image
        elif(event.key == 'm'): mark_dots = not mark_dots
        update_view()

    fig.canvas.callbacks.connect('key_press_event', on_press)

    update_view()
    while not done:
        plt.pause(0.001)
        if not plt.fignum_exists(1):
            done = True


