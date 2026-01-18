# https://www.codingame.com/contribute/view/6224d52ad5295355fd7d7d48a5a5a8188a53
from math import tan, cos, pi, ceil, floor
# X, Y, ANGLE = (200, 200, 0)
# level_file = open('maze/level_1.txt', 'r')
# M = [line.strip() for line in level_file.readlines()]
# n = len(M)
X, Y, ANGLE = map(int, input().split())
n = int(input())
M = [input() for _ in range(n)]
TAN = lambda a: tan(a/180*pi)
COS = lambda a: cos(a/180*pi)

def dist(X, Y, x, y):
    return ((X-x)**2 + (Y-y)**2)**.5

def collision(X, Y, angle):
    if angle <= -180:
        angle += 360
    elif angle > 180:
        angle -= 360
    MIN = float("inf")
    # h-walls
    if angle != 0 and angle != 180:
        IT = 1/TAN(angle)
        b = angle < 0
        y0 = floor(Y/100)*100 if b else ceil(Y/100)*100
        x0 = X + (y0 - Y)*IT
        while True:
            i, j = y0//100 - 1*b, int(x0/100)
            if not 0 <= i < n or not 0 <= j < n or M[i][j] != ".":
                break
            y0 += 100*(-1)**b
            x0 += 100*IT*(-1)**b
        MIN = dist(X, Y, x0, y0)
        horizontal = True
    # v-walls
    if angle != 90 and angle != -90:
        T = TAN(angle)
        b = angle > 90 or angle < -90
        x0 = floor(X/100)*100 if b else ceil(X/100)*100
        y0 = Y + (x0 - X)*T
        while True:
            i, j = int(y0/100), x0//100 - 1*b
            if not 0 <= i < n or not 0 <= j < n or M[i][j] != ".":
                break
            x0 += 100*(-1)**b
            y0 += 100*T*(-1)**b
        d = dist(X, Y, x0, y0)
        if d < MIN:
            MIN = d
            horizontal = False
    return MIN, horizontal

def draw():
    Values = []
    for angle in range(ANGLE -30, ANGLE + 31):
        MIN, horizontal = collision(X, Y, angle)
        h = round(1500/(MIN*COS(ANGLE - angle)))
        pix = min(15, h*2 + 1)
        fill = (15 - pix)//2
        v = [",", "."][horizontal]
        Values.append(fill*" " + pix*v + fill*" ")
    t = "\n".join("".join(row) for row in zip(*Values))
    print(t)

draw()