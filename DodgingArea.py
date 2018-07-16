import numpy as np

DELTA=10

SCALE=2*DELTA+2

def init_area():
    narray=[]
    for i in range(DELTA):
        narray.append([0]*SCALE)
    narray.append([0] * DELTA + [2, 2] + [0] * DELTA)
    narray.append([0] * DELTA + [2, 2] + [0] * DELTA)
    for i in range(DELTA):
        narray.append([0]*SCALE)
    return np.array(narray)

def wash_area(area, lu_p, x1, x2, y1, y2):
    for i in range(SCALE):
        for j in range(SCALE):
            # 没子弹，检查
            if area[i][j]==0:
                # 判断
                if (lu_p[0]+j>=x1)and(lu_p[0]+j<=x2-1)and(lu_p[1]+i>=y1)and(lu_p[1]+i<=y2-1):
                    area[i][j]=1
# 激光
def wash_area_laser(area, lu_p, cp1, cp2, cp3, cp4):
    for i in range(SCALE):
        for j in range(SCALE):
            point=area[i][j]
            # 没子弹，检查
            if point==0:
                # 判断
                if is_in_rectangle((lu_p[0]+j, lu_p[1]+i), cp1, cp2, cp3, cp4):
                    area[i][j]=1

def is_in_rectangle(p, cp1, cp2, cp3, cp4):
    return (triangle_area(cp1, cp2, cp3) + triangle_area(cp1, cp3, cp4))==(triangle_area(p, cp1, cp2) + triangle_area(p, cp2, cp3) + triangle_area(p, cp3, cp4) + triangle_area(p, cp4, cp1))

def triangle_area(a, b, c):
    return abs((a[0] * b[1] + b[0] * c[1] + c[0] * a[1] - b[0] * a[1]  - c[0] * b[1] - a[0] * c[1]) / 2.0)
