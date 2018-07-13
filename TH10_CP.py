import os
os.environ["PYSDL2_DLL_PATH"] = ".\\"
from sdl2 import *
from win32gui import *
from win32process import *
from win32api import *
from win32con import *
import ctypes

HANDLE=0

PROCESS=0

class rectag(object):
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

def get_enemy_data():
    global PROCESS
    enemy_list=[]
    base, obj_base, obj_addr, obj_next = ctypes.c_int(), ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
    mydll = ctypes.windll.LoadLibrary(".\\kernel32.dll")
    mydll.ReadProcessMemory(int(PROCESS), 0x00477704, ctypes.byref(base), 4, None)
    mydll.ReadProcessMemory(int(PROCESS), base.value + 0x58, ctypes.byref(obj_base), 4, None)
    while True:
        mydll.ReadProcessMemory(int(PROCESS), obj_base.value, ctypes.byref(obj_addr), 4, None)
        mydll.ReadProcessMemory(int(PROCESS), obj_base.value + 0x4, ctypes.byref(obj_next), 4, None)
        obj_addr.value+=0x103c
        t=ctypes.c_uint()
        mydll.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x1444, ctypes.byref(t), 4, None)
        if (t.value & 0x40)==0:
            mydll.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x1444, ctypes.byref(t), 4, None)
            if (t.value & 0x12)==0:
                x, y, w, h=ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
                mydll.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x2c, ctypes.byref(x), 4, None)
                mydll.ReadProcessMemory(int(PROCESS), obj_addr.value + 0x30, ctypes.byref(y), 4, None)
                mydll.ReadProcessMemory(int(PROCESS), obj_addr.value + 0xb8, ctypes.byref(w), 4, None)
                mydll.ReadProcessMemory(int(PROCESS), obj_addr.value + 0xbc, ctypes.byref(h), 4, None)
                rec=rectag(x.value, y.value, w.value, h.value)
                enemy_list.append(rec)
        if obj_next.value==0:
            break
        obj_base.value=obj_next.value
    return enemy_list

def find_TH10():
    global HANDLE
    HANDLE = FindWindow(None, u"东方风神录 ～ Mountain of Faith. ver 1.00a ")
    return True if HANDLE!=0 else False

if __name__=="__main__":
    enemy_list=[]
    if not find_TH10():
        print("你没开风神录")
    else:
        global PROCESS
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
            while find_TH10() and running:
                while SDL_PollEvent(ctypes.byref(event)) != 0:
                    if event.type == SDL_QUIT:
                        running = False
                        break
                SDL_SetRenderDrawColor(renderer, 255, 255, 255, 0);
                SDL_RenderClear(renderer);
                SDL_SetRenderDrawColor(renderer, 255, 0, 0, 0);
                for enemy in get_enemy_data():
                    rect = SDL_Rect(int(enemy.get_x() - 0.5 * enemy.get_w() + 200), int(enemy.get_y() - 0.5 * enemy.get_h()), int(enemy.get_w()), int(enemy.get_h()))
                    SDL_RenderDrawRect(renderer, rect)
                SDL_RenderPresent(renderer);
                SDL_Delay(16);
            print("风神录关闭")
            SDL_DestroyRenderer(renderer)
            SDL_DestroyWindow(window)
            SDL_Quit()