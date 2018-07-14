import os
os.environ["PYSDL2_DLL_PATH"] = ".\\"
from sdl2 import *
from win32gui import *
from win32process import *
from win32api import *
from win32con import *
import ctypes
from math import *

HANDLE=0

PROCESS=0

DLL = ctypes.windll.LoadLibrary(".\\kernel32.dll")

class Item(object):
    def __init__(self, x, y):
        self.__x=x
        self.__y=y

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

class Enemy(object):
    def __init__(self, x, y, w, h):
        self.__x=x
        self.__y=y
        self.__w=w
        self.__h=h

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_w(self):
        return self.__w

    def get_h(self):
        return self.__h

    def __str__(self):
        return "Reactangle: [x:"+str(self.__x)+" y:"+str(self.__y)+" w:"+str(self.__w)+" h:"+str(self.__h)+"]"

class Bullet(object):
    def __init__(self, x, y, w, h, dx, dy):
        self.__x=x
        self.__y=y
        self.__w=w
        self.__h=h
        self.__dx=dx
        self.__dy=dy

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_w(self):
        return self.__w

    def get_h(self):
        return self.__h

    def get_dx(self):
        return self.__dx

    def get_dy(self):
        return self.__dy

class Laser(object):
    def __init__(self, x, y, w, h, arc):
        self.__x=x
        self.__y=y
        self.__w=w
        self.__h=h
        self.__arc=arc

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_w(self):
        return self.__w

    def get_h(self):
        return self.__h

    def get_arc(self):
        return self.__arc

def get_item_data():
    global PROCESS
    item_list=[]
    base = ctypes.c_int()
    DLL.ReadProcessMemory(int(PROCESS), 0x00477818, ctypes.byref(base), 4, None)
    if base.value==0:
        return item_list
    esi, ebp=ctypes.c_int(), ctypes.c_int()
    esi.value=base.value+0x14
    ebp.value=esi.value+0x3b0
    for i in range(2000):
        eax=ctypes.c_int()
        DLL.ReadProcessMemory(int(PROCESS), ebp.value + 0x2c, ctypes.byref(eax), 4, None)
        if eax.value!=0:
            x, y = ctypes.c_float(), ctypes.c_float()
            DLL.ReadProcessMemory(int(PROCESS), ebp.value - 0x4, ctypes.byref(x), 4, None)
            DLL.ReadProcessMemory(int(PROCESS), ebp.value, ctypes.byref(y), 4, None)
            item=Item(x, y)
            item_list.append(item)
        ebp.value+=0x3f0
    return item_list

def get_enemy_data():
    global PROCESS
    enemy_list=[]
    base, obj_base, obj_addr, obj_next = ctypes.c_int(), ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
    DLL.ReadProcessMemory(int(PROCESS), 0x00477704, ctypes.byref(base), 4, None)
    if base.value==0:
        return enemy_list
    DLL.ReadProcessMemory(int(PROCESS), base.value + 0x58, ctypes.byref(obj_base), 4, None)
    if obj_base.value!=0:
        while True:
            DLL.ReadProcessMemory(int(PROCESS), obj_base.value, ctypes.byref(obj_addr), 4, None)
            DLL.ReadProcessMemory(int(PROCESS), obj_base.value + 0x4, ctypes.byref(obj_next), 4, None)
            obj_addr.value += 0x103c
            t = ctypes.c_uint()
            DLL.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x1444, ctypes.byref(t), 4, None)
            if (t.value & 0x40) == 0:
                DLL.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x1444, ctypes.byref(t), 4, None)
                if (t.value & 0x12) == 0:
                    x, y, w, h = ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
                    DLL.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x2c, ctypes.byref(x), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x30, ctypes.byref(y), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), obj_addr.value + 0xb8, ctypes.byref(w), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), obj_addr.value + 0xbc, ctypes.byref(h), 4, None)
                    enemy = Enemy(x.value, y.value, w.value, h.value)
                    enemy_list.append(enemy)
            if obj_next.value == 0:
                break
            obj_base.value = obj_next.value
    return enemy_list

def get_player_data():
    global PROCESS
    player_list=[]
    x, y = ctypes.c_float(), ctypes.c_float()
    obj_base = ctypes.c_int()
    DLL.ReadProcessMemory(int(PROCESS), 0x00477834, ctypes.byref(obj_base), 4, None)
    if obj_base.value==0:
        return player_list
    DLL.ReadProcessMemory(int(PROCESS), obj_base.value + 0x3c0, ctypes.byref(x), 4, None)
    DLL.ReadProcessMemory(int(PROCESS), obj_base.value + 0x3c4, ctypes.byref(y), 4, None)
    player = Item(x, y)
    player_list.append(player)
    return player_list

def get_bullet_data():
    global PROCESS
    bullet_list=[]
    base=ctypes.c_int()
    DLL.ReadProcessMemory(int(PROCESS), 0x004776f0, ctypes.byref(base), 4, None)
    if base.value==0:
        return bullet_list
    ebx=ctypes.c_int()
    ebx.value=base.value+0x60
    for i in range(2000):
        edi, bp=ctypes.c_int(), ctypes.c_int()
        edi.value=ebx.value+0x400;
        DLL.ReadProcessMemory(int(PROCESS), edi.value + 0x46, ctypes.byref(bp), 4, None)
        bp.value=bp.value & 0x0000ffff
        if bp.value!=0:
            eax = ctypes.c_int()
            DLL.ReadProcessMemory(int(PROCESS), 0x00477810, ctypes.byref(eax), 4, None)
            if eax.value!=0:
                DLL.ReadProcessMemory(int(PROCESS), eax.value + 0x58, ctypes.byref(eax), 4, None)
                if (eax.value & 0x00000400) == 0:
                    x, y, w, h, dx, dy = ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
                    DLL.ReadProcessMemory(int(PROCESS), ebx.value + 0x3c0, ctypes.byref(dx), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), ebx.value + 0x3c4, ctypes.byref(dy), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), ebx.value + 0x3b4, ctypes.byref(x), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), ebx.value + 0x3b8, ctypes.byref(y), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), ebx.value + 0x3f0, ctypes.byref(w), 4, None)
                    DLL.ReadProcessMemory(int(PROCESS), ebx.value + 0x3f4, ctypes.byref(h), 4, None)
                    bullet = Bullet(x.value, y.value, w.value, h.value, dx.value / 2.0, dy.value / 2.0)
                    bullet_list.append(bullet)
        ebx.value+=0x7f0
    return bullet_list

def get_laser_data():
    global PROCESS
    laser_list=[]
    base=ctypes.c_int()
    DLL.ReadProcessMemory(int(PROCESS), 0x0047781c, ctypes.byref(base), 4, None)
    if base.value==0:
        return laser_list
    esi, ebx=ctypes.c_int(), ctypes.c_int()
    DLL.ReadProcessMemory(int(PROCESS), base.value + 0x18, ctypes.byref(esi), 4, None)
    while True:
        DLL.ReadProcessMemory(int(PROCESS), esi.value + 0x8, ctypes.byref(ebx), 4, None)
        x, y, w, h, arc = ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
        DLL.ReadProcessMemory(int(PROCESS), esi.value + 0x24, ctypes.byref(x), 4, None)
        DLL.ReadProcessMemory(int(PROCESS), esi.value + 0x28, ctypes.byref(y), 4, None)
        DLL.ReadProcessMemory(int(PROCESS), esi.value + 0x3c, ctypes.byref(arc), 4, None)
        DLL.ReadProcessMemory(int(PROCESS), esi.value + 0x40, ctypes.byref(h), 4, None)
        DLL.ReadProcessMemory(int(PROCESS), esi.value + 0x44, ctypes.byref(w), 4, None)
        laser=Laser(x.value, y.value, w.value/2.0, h.value, arc.value)
        laser_list.append(laser)
        if ebx.value==0:
            break
        esi.value=ebx.value
    return laser_list

def PointRotate(cx, cy, x, y, arc):
	_x = cx + (x - cx) * cos(arc) - (y - cy) * sin(arc)
	_y = cy + (x - cx) * sin(arc) + (y - cy) * cos(arc)
	return _x, _y

def find_TH10():
    global HANDLE
    HANDLE = FindWindow(None, u"东方风神录 ～ Mountain of Faith. ver 1.00a ")
    return True if HANDLE!=0 else False

if __name__=="__main__":
    enemy_list=[]
    if not find_TH10():
        print("你没开风神录")
    else:
        hid, pid = GetWindowThreadProcessId(HANDLE)
        PROCESS = OpenProcess(PROCESS_VM_READ, True, pid)
        if PROCESS==0:
            print("打开进程失败")
        else:
            window = SDL_CreateWindow(b"TH10_CP",
                                      SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                      400, 480, SDL_WINDOW_SHOWN)
            renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)
            running = True
            event = SDL_Event()
            while True:
                if not find_TH10():
                    print("风神录关闭，显示器将随之关闭")
                    SDL_DestroyRenderer(renderer)
                    SDL_DestroyWindow(window)
                    SDL_Quit()
                    break
                if not running:
                    print("显示器关闭")
                    SDL_DestroyRenderer(renderer)
                    SDL_DestroyWindow(window)
                    SDL_Quit()
                    break
                while SDL_PollEvent(ctypes.byref(event)) != 0:
                    if event.type == SDL_QUIT:
                        running = False
                        break
                SDL_SetRenderDrawColor(renderer, 255, 255, 255, 0)
                SDL_RenderClear(renderer)
                SDL_SetRenderDrawColor(renderer, 0, 255, 0, 0)
                for item in get_item_data():
                    rect = SDL_Rect(int(item.get_x().value) +197, int(item.get_y().value) - 3, 6, 6)
                    SDL_RenderDrawRect(renderer, rect)
                SDL_SetRenderDrawColor(renderer, 255, 0, 0, 0)
                for enemy in get_enemy_data():
                    rect = SDL_Rect(int(enemy.get_x() - 0.5 * enemy.get_w() + 200), int(enemy.get_y() - 0.5 * enemy.get_h()), int(enemy.get_w()), int(enemy.get_h()))
                    SDL_RenderDrawRect(renderer, rect)
                for bullet in get_bullet_data():
                    rect = SDL_Rect(int(bullet.get_x() - 0.5 * bullet.get_w() + 200), int(bullet.get_y() - 0.5 * bullet.get_h()), int(bullet.get_w()), int(bullet.get_h()))
                    SDL_RenderDrawRect(renderer, rect)
                for laser in get_laser_data():
                    x1 = 200 + laser.get_x() - 0.5 * laser.get_w()
                    y1 = laser.get_y()
                    x2 = x1 + laser.get_w()
                    y2 = y1
                    x3 = x1
                    y3 = y2 + laser.get_h()
                    x4 = x2
                    y4 = y3
                    cx = (x1 + x2) * 0.5
                    cy = (y1 + y2) * 0.5
                    arc = laser.get_arc() - 3.1415926 * 5 / 2
                    x1, y1 = PointRotate(cx, cy, x1, y1, arc)
                    x2, y2 = PointRotate(cx, cy, x2, y2, arc)
                    x3, y3 = PointRotate(cx, cy, x3, y3, arc)
                    x4, y4 = PointRotate(cx, cy, x4, y4, arc)
                    SDL_RenderDrawLine(renderer, int(x1), int(y1), int(x2), int(y2))
                    SDL_RenderDrawLine(renderer, int(x2), int(y2), int(x4), int(y4))
                    SDL_RenderDrawLine(renderer, int(x3), int(y3), int(x4), int(y4))
                    SDL_RenderDrawLine(renderer, int(x1), int(y1), int(x3), int(y3))
                SDL_SetRenderDrawColor(renderer, 0, 0, 255, 0)
                for player in get_player_data():
                    rect = SDL_Rect(int(player.get_x().value) +198, int(player.get_y().value) - 2, 4, 4)
                    SDL_RenderDrawRect(renderer, rect)
                SDL_RenderPresent(renderer)
                SDL_Delay(16)