from matplotlib import pyplot as plt
import subprocess
import os

def get_values(filename):
    x = []
    y = []
    x0 = []
    y0 = []

    p = subprocess.Popen(["calc_nifs3.exe"], stdin=open(filename, "r"), stdout=subprocess.PIPE)

    while True:
        line = p.stdout.readline()
        if not line:
            break
        if "err" in line.rstrip().decode("utf-8"): 
            print(line.rstrip().decode("utf-8"))
            continue

        a, b = line.rstrip().decode("utf-8").split()
        if(abs(float(a)) < 1000 and abs(float(b)) < 1000):
            x.append(float(a))
            y.append(float(b))
        else:
            print("ERROR at", a, b)
            # p.kill()
            # return get_values(filename, _from, _to, _step)

    try:
        file = open(filename, "r")
        for line in file:
            try:
                tx, ty = line.split()
            except:
                continue
            x0.append(float(tx))
            y0.append(float(ty))
        file.close()
    except:
        pass

    return x, y, x0, y0


x = []
y = []
x0 = []
y0 = [] 
for file in os.listdir("./points"):
    if file.endswith(".in"):
        tx, ty, tx0, ty0 = get_values(f"points/{file}")
        x += tx
        y += ty
        x0 += tx0
        y0 += ty0

        plt.plot(tx, ty)

# plt.scatter(x0, y0, color = "red")
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')
plt.show()

