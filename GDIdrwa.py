import math
import pymem
import win32api
import win32gui
import win32process
import time

from GDIUtils import drawRect
from GDIOverlay import OverlayWindow


WindowHandle = win32gui.FindWindow(None, "Counter-Strike 2")
if not WindowHandle:
    print("未找到Counter-Strike 2游戏窗口")
    # 尝试使用 国服 的窗口名
    print("尝试使用 反恐精英：全球攻势 窗口名")
    WindowHandle = win32gui.FindWindow(None, "反恐精英：全球攻势")
    
if not WindowHandle:
    # 如果还是没有找到，可能是游戏未启动或窗口名不正确
    print("没有找到游戏窗口")
    exit(1)
    
# 获取窗口的线程和进程ID
ThreadId, ProcessId = win32process.GetWindowThreadProcessId(WindowHandle)
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
ProcessHandle = pymem.process.open(ProcessId, True, PROCESS_ALL_ACCESS)
if not ProcessHandle:
    print("无法打开进程，请确保游戏已启动。")
    exit(1)
client_dll = pymem.process.module_from_name(ProcessHandle, "client.dll").lpBaseOfDll

if not client_dll:
    print("无法获取 client.dll 基址，请确认游戏已启动且窗口名正确。")
    exit(1)

client_dll_offset_human = 0x1865288
client_dll_offset_y = 0x1A794B0
client_dll_offset_x = 0X1A78E24
x_offset = 0xDB8
y_offset = 0xDBC
z_offset = 0xDC0
blood_offset = 0xAB4

brush = win32gui.CreateSolidBrush(win32api.RGB(0, 0, 255))

human_array = pymem.memory.read_longlong(ProcessHandle, client_dll + client_dll_offset_human)
my_offset_way1 = 0x8
my_offset_way2 = 0x0
my_array_way1 = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset_way1)
my_blood_way1 = pymem.memory.read_int(ProcessHandle, my_array_way1 + blood_offset)
my_array = my_array_way1
my_offset = my_offset_way1
isEight = True
if my_blood_way1 == 0:
    my_array_way2 = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset_way2)
    my_blood_way2 = pymem.memory.read_int(ProcessHandle, my_array_way2 + blood_offset)
    my_array = my_array_way2
    my_offset = my_offset_way2
    isEight = False

# 获取屏幕分辨率
screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)

def draw_callback(hdc):
    # 获取窗口位置
    try:
        rect = win32gui.GetWindowRect(WindowHandle)
    except:
        print("无法获取窗口位置，请确保游戏窗口已打开。")
        return

    left, top, right, bottom = rect
    width = right - left
    height = bottom - top

    # 读取自己坐标
    my_x = pymem.memory.read_float(ProcessHandle, my_array + x_offset)
    my_y = pymem.memory.read_float(ProcessHandle, my_array + y_offset)
    my_z = pymem.memory.read_float(ProcessHandle, my_array + z_offset)
    fov_y = pymem.memory.read_float(ProcessHandle, client_dll + client_dll_offset_y)
    fov_x = pymem.memory.read_float(ProcessHandle, client_dll + client_dll_offset_x)

    count = 1
    multipliers = [0x8, 0x2] if isEight else [0x2, 0x8]
    for i in range(1, 20):
        if not isEight and i == 19:
            break
        human_offset = count * multipliers[i % 2]
        count += 1
        other_array = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset + human_offset)
        try:
            other_blood = pymem.memory.read_int(ProcessHandle, other_array + blood_offset)
        except:
            continue
        if other_blood == 0:
            continue
        other_x = pymem.memory.read_float(ProcessHandle, other_array + x_offset)
        other_y = pymem.memory.read_float(ProcessHandle, other_array + y_offset)
        other_z = pymem.memory.read_float(ProcessHandle, other_array + z_offset)

        sub_y = other_y - my_y
        sub_x = other_x - my_x
        sub_z = other_z - my_z
        dis_on_top = math.sqrt((other_x - my_x) ** 2 + (other_y - my_y) ** 2)
        dis_on_space = math.sqrt((other_x - my_x) ** 2 + (other_y - my_y) ** 2 + (other_z - my_z) ** 2)

        # 下面的象限判断和坐标计算与原来一致，只是把 drawRect 换成 hdc 版本
        # 以第一象限为例，其他象限同理
        #第一象限
        # if other_y > my_y and other_x > my_x:
        #     angle_DW_x = math.degrees(math.atan(sub_y / sub_x))
        #     angle_DZ_x = fov_x - angle_DW_x
        #     dis_DZ_x = math.sin(math.radians(angle_DZ_x)) * dis_on_top
        #     dis_WZ_x = math.sqrt(dis_on_top ** 2 - dis_DZ_x ** 2) * 1.3
        #     dis_x_screen = dis_DZ_x / dis_WZ_x * width / 2 + (width / 2)
        #     if -55 < angle_DZ_x < 50:
        #         angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
        #         if other_z > my_z:
        #             angle_DZ_y = fov_y + abs(angle_DW_space)
        #         elif other_z < my_z:
        #             angle_DZ_y = fov_y - abs(angle_DW_space)
        #         dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space
        #         dis_WZ_y = math.sqrt(dis_on_space ** 2 - dis_DZ_y ** 2) * 0.80
        #         dis_y_screen = (height / 2) - dis_DZ_y / dis_WZ_y * height / 2
        #         drawRect(hdc, dis_x_screen, dis_y_screen + 10, dis_on_space, 1, brush)
            
        #第一象限
        if other_y>my_y and other_x>my_x:
            # print("壹")
            '''========X计算========'''
            # 敌相对于我X轴的角度
            angle_DW_x = math.degrees(math.atan(sub_y / sub_x))
            # 敌人相对于准星的角度（横向）
            angle_DZ_x=fov_x-angle_DW_x
            # 敌人与准星的横向距离(游戏中_横向)
            dis_DZ_x=math.sin(math.radians(angle_DZ_x)) * dis_on_top
            # 我与准星的距离（游戏中_横向）
            dis_WZ_x= math.sqrt(math.pow(dis_on_top,2)-math.pow(dis_DZ_x,2)) *1.3
            # 敌人在屏幕上的X坐标计算
            dis_x_screen=dis_DZ_x/dis_WZ_x*screen_width/2+(screen_width/2)
            #如果敌人相对于准星角度 在 -55~50才绘制（横向）
            if angle_DZ_x>-55 and angle_DZ_x<50:
                '''=========Y计算======='''
                # 敌相对于我空间平面角度
                angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z>my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                #如果敌人在我下方
                elif other_z<my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (screen_height / 2) - dis_DZ_y / dis_WZ_y * screen_height / 2
                #绘制方框
                drawRect(hdc,dis_x_screen+left,dis_y_screen+top+10,dis_on_space,1,brush)
        #第二象限
        elif other_y>my_y and other_x<my_x:
            # print("贰")
            '''========X计算========'''
            # 敌相对于我X轴的角度
            angle_DW_x = math.degrees(math.atan(sub_y / sub_x))
            # 敌人相对于准星的角度（横向）
            angle_DZ_x = fov_x - angle_DW_x-180
            # 敌人与准星的横向距离(游戏中_横向)
            dis_DZ_x = math.sin(math.radians(angle_DZ_x)) * dis_on_top
            # 我与准星的距离（游戏中_横向）
            dis_WZ_x = math.sqrt(math.pow(dis_on_top, 2) - math.pow(dis_DZ_x, 2)) * 1.3
            # 敌人在屏幕上的X坐标计算
            dis_x_screen =dis_DZ_x / dis_WZ_x * screen_width / 2 + (screen_width / 2)
            # 如果敌人相对于准星角度 在 以下范围 才绘制（横向）
            # print(angle_DZ_x)
            if (angle_DZ_x > -54 and angle_DZ_x < 50) or (angle_DZ_x>-360 and angle_DZ_x<-305) :
                # 敌相对于我空间平面角度
                angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z > my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                # 如果敌人在我下方
                elif other_z < my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (screen_height / 2) - dis_DZ_y / dis_WZ_y * screen_height / 2
                # 绘制方框
                drawRect(hdc, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)
        #第三象限（类似二象限）
        elif other_y<my_y and other_x<my_x:
            # print("叁")
            '''========X计算========'''
            # 敌相对于我X轴的角度
            angle_DW_x = math.degrees(math.atan(sub_y / sub_x))
            # 敌人相对于准星的角度（横向）
            angle_DZ_x = fov_x - angle_DW_x - 180
            # 敌人与准星的横向距离(游戏中_横向)
            dis_DZ_x = math.sin(math.radians(angle_DZ_x)) * dis_on_top
            # 我与准星的距离（游戏中_横向）
            dis_WZ_x = math.sqrt(math.pow(dis_on_top, 2) - math.pow(dis_DZ_x, 2)) * 1.3
            # 敌人在屏幕上的X坐标计算
            dis_x_screen = dis_DZ_x / dis_WZ_x * screen_width / 2 + (screen_width / 2)
            # 如果敌人相对于准星角度 在 以下范围 才绘制（横向）
            if (angle_DZ_x > -410 and angle_DZ_x < -310) or (angle_DZ_x > -50 and angle_DZ_x < 0):
                # 敌相对于我空间平面角度
                angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z > my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                # 如果敌人在我下方
                elif other_z < my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (screen_height / 2) - dis_DZ_y / dis_WZ_y * screen_height / 2
                # 绘制方框
                drawRect(hdc, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)
        # 第四象限
        elif other_y < my_y and other_x > my_x:
            # print("肆")
            '''========X计算========'''
            # 敌相对于我X轴的角度
            angle_DW_x = math.degrees(math.atan(sub_y / sub_x))
            # 敌人相对于准星的角度（横向）s
            angle_DZ_x = fov_x - angle_DW_x
            # 敌人与准星的横向距离(游戏中_横向)
            dis_DZ_x = math.sin(math.radians(angle_DZ_x)) * dis_on_top
            # 我与准星的距离（游戏中_横向）
            dis_WZ_x = math.sqrt(math.pow(dis_on_top, 2) - math.pow(dis_DZ_x, 2)) * 1.3
            # 敌人在屏幕上的X坐标计算
            dis_x_screen = dis_DZ_x / dis_WZ_x * screen_width / 2 + (screen_width / 2)
            # 如果敌人相对于准星角度 在 -55~50才绘制（横向）
            if angle_DZ_x > -55 and angle_DZ_x < 50:
                '''=========Y计算======='''
                # 敌相对于我空间平面角度
                angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z > my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                # 如果敌人在我下方
                elif other_z < my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (screen_height / 2) - dis_DZ_y / dis_WZ_y * screen_height / 2
                # 绘制方框
                drawRect(hdc, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)
  
        # 其余象限同理，照搬原有逻辑，drawRect(hdc, ...)即可

# 创建Overlay窗口
overlay = OverlayWindow(screen_width, screen_height, draw_callback)
print("Overlay窗口已创建，开始监听游戏数据...")
# 主循环：不断刷新Overlay窗口
while True:
    overlay.refresh()
    win32gui.PumpWaitingMessages()
    time.sleep(0.05)  # 控制刷新频率，避免过高的CPU占用
    # 这里可以添加其他逻辑，比如检测游戏状态变化等  
    