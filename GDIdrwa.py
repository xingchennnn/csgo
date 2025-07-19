import math
import pymem
import win32api
import win32gui
import win32process
import time

from GDIUtils import drawRect
from GDIOverlay import OverlayWindow
from math import asin
    
def safe_asin(x):
    return asin(max(-1.0, min(1.0, x)))


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

client_dll_offset_human = 0x1866298 # 人物数组偏移
client_dll_offset_y = 0x1A52314 # 方向y偏移 
client_dll_offset_x = 0X1A52318 # 方向x偏移 x = y + 4
x_offset = 0xDB8 # 角色 X 轴坐标偏移
y_offset = 0xDBC # 角色 Y 轴坐标偏移
z_offset = 0xDC0 # 角色 Z 轴坐标偏移
blood_offset = 0xAB4 # 血量偏移
camp_offset = 0xE68 # 阵营偏移

camera_offset_x = 0x1A6EB60 # 视角轴x偏移
camera_offset_y = 0x1A6EB84 # 视角轴y偏移
camera_offset_z = 0x1A6EB68 # 视角轴z偏移

brush = win32gui.CreateSolidBrush(win32api.RGB(0, 0, 255))

human_array = pymem.memory.read_longlong(ProcessHandle, client_dll + client_dll_offset_human)  # 读取人物数组 基址

my_offset_way1 = 0x8 # 8人模式下第一个角色偏移
my_offset_way2 = 0x0 # 8人模式下第二个角色偏移

my_array_way1 = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset_way1 )  # 读取第一个角色数组    基址+偏移 = 我的角色数组基址

my_blood_way1 = pymem.memory.read_int(ProcessHandle, my_array_way1 + blood_offset)  # 读取第一个角色血量    我的角色数组基址+血量偏移 = 我的角色血量

my_array = my_array_way1  # 选择第一个角色数组
my_offset = my_offset_way1  # 选择第一个角色偏移

isEight = True  # 是否为8人模式
if my_blood_way1 == 0 or my_blood_way1 > 100 or my_blood_way1 < 0:  # 尝试读取第二个角色
    my_array_way2 = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset_way2)  # 读取第二个角色数组   
    my_blood_way2 = pymem.memory.read_int(ProcessHandle, my_array_way2 + blood_offset)  # 读取第二个角色血量    
    my_array = my_array_way2  # 选择第二个角色数组
    my_offset = my_offset_way2  # 选择第二个角色偏移
    isEight = False
    
    
game_width = win32api.GetSystemMetrics(0)  # 获取屏幕宽度
game_height = win32api.GetSystemMetrics(1)  # 获取屏幕高度    


def draw_callback(hdc):
    # 获取窗口位置
    try:
        rect = win32gui.GetWindowRect(WindowHandle) # 获窗口针对屏幕原点的位置 
    except:
        print("无法获取窗口位置，请确保游戏窗口已打开。")
        return

    # left, top, right, bottom = rect
    # game_width = right - left
    # game_height = bottom - top

    # 获取游戏窗口大小
    try:
        rect = win32gui.GetWindowRect(WindowHandle)
        left, top, right, bottom = rect
        game_width = right - left
        game_height = bottom - top
    except:
        print("无法获取游戏窗口大小，使用默认屏幕分辨率")
        game_width = win32api.GetSystemMetrics(0)
        game_height = win32api.GetSystemMetrics(1)
    # width = right - left
    # height = bottom - top
    # 修改坐标读取代码段（约 79-84 行）
    
    try:
        # my_x = pymem.memory.read_float(ProcessHandle, my_array + x_offset)  # 读取我的角色 X 坐标
        # my_y = pymem.memory.read_float(ProcessHandle, my_array + y_offset)  # 读取我的角色 Y 坐标
        # my_z = pymem.memory.read_float(ProcessHandle, my_array + z_offset)  # 读取我的角色 Z 坐标
        
        my__z = pymem.memory.read_float(ProcessHandle, my_array + z_offset)  # 读取我的角色 Z 坐标
        my_x = pymem.memory.read_float(ProcessHandle, client_dll + camera_offset_x)  # 读取我的角色 X 坐标
        my_y = pymem.memory.read_float(ProcessHandle, client_dll + camera_offset_y)  # 读取我的角色 Y 坐标
        my_z = pymem.memory.read_float(ProcessHandle, client_dll + camera_offset_z)  # 读取我的角色 Z 坐标
        fov_y = pymem.memory.read_float(ProcessHandle, client_dll + client_dll_offset_y)  # 读取视角 Y 坐标
        fov_x = pymem.memory.read_float(ProcessHandle, client_dll + client_dll_offset_x)  # 读取视角 X 坐标
        my_z = my_z + -63.84  # 修正视角 Y 坐标
        
        my_camp = pymem.memory.read_int(ProcessHandle, my_array + camp_offset)  # 读取阵营  0 未分配  2T  3CT
        
        # print(f"我的阵营：{my_camp}")
         # 新增有效性检查
        if math.isnan(fov_y) or math.isnan(fov_x):
            raise ValueError("fov_y/fov_x 读取到 NaN 值")
    except (pymem.exception.MemoryReadError, ValueError) as e:
        print(f"FOV 视角 读取失败: {e}")
        return


    count = 1
    multipliers = [0x8, 0x2] if isEight else [0x2, 0x8]  # 8人模式下角色偏移量  
    for i in range(1, 20):
        if not isEight and i == 19:
            break
        human_offset = count * multipliers[i % 2] # 选择角色偏移量
        # human_offset = count * 10 # 选择角色偏移量
        
        count += 1 # 角色计数
        other_array = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset + human_offset)  # 读取其他角色数组 基址+我的偏移 + 不同角色偏移 = 其他角色数组基址
        
        # 获取其他角色阵营
        # other_camp = pymem.memory.read_int(ProcessHandle, other_array + camp_offset)
        # print(f"其他阵营：{other_camp}")
        # other_camp = 0  # 阵营暂时不显示
        # if other_camp == my_camp:  # 如果阵营相同则跳过
        #     continue
        
        
        try:
            other_blood = pymem.memory.read_int(ProcessHandle, other_array + blood_offset) # 读取其他角色血量
        except:
            continue
        if other_blood == 0 or other_blood > 100 or other_blood < 0:  # 如果血量为0或大于100或小于1则跳过
            continue
        #获取敌人坐标
        other_x = pymem.memory.read_float(ProcessHandle, other_array + x_offset)
        other_y = pymem.memory.read_float(ProcessHandle, other_array + y_offset)
        other_z = pymem.memory.read_float(ProcessHandle, other_array + z_offset)
        # 计算距离  
        sub_y = other_y - my_y
        sub_x = other_x - my_x
        sub_z = other_z - my_z
        
        # 计算距离
        dis_on_top = math.sqrt((other_x - my_x) ** 2 + (other_y - my_y) ** 2) # 计算距离
        dis_on_space = math.sqrt((other_x - my_x) ** 2 + (other_y - my_y) ** 2 + (other_z - my_z) ** 2) # 计算距离

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
            dis_x_screen=dis_DZ_x / dis_WZ_x * game_width / 2 + (game_width/2) 
            #如果敌人相对于准星角度 在 -55~50才绘制（横向）
            if angle_DZ_x>-55 and angle_DZ_x<50:
                '''=========Y计算======='''
                # 敌相对于我空间平面角度
                if sub_z == 0:
                    angle_DW_space = 0  # 当z轴相同时，角度设为0
                else:
                    angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z>=my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                #如果敌人在我下方
                elif other_z<my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space  # 第一象限
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (game_height / 2) - dis_DZ_y / dis_WZ_y * (game_height / 2)
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
            dis_x_screen =dis_DZ_x / dis_WZ_x * game_width / 2 + (game_width / 2)
            # 如果敌人相对于准星角度 在 以下范围 才绘制（横向）
            # print(angle_DZ_x)
            if (angle_DZ_x > -54 and angle_DZ_x < 50) or (angle_DZ_x>-360 and angle_DZ_x<-305) :
                '''=========Y计算======='''
                # 敌相对于我空间平面角度
                if sub_z == 0:
                    angle_DW_space = 0  # 当z轴相同时，角度设为0
                else:
                    angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z >= my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                # 如果敌人在我下方
                elif other_z < my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space # 第二象限
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (game_height / 2) - dis_DZ_y / dis_WZ_y * game_height / 2
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
            dis_x_screen = dis_DZ_x / dis_WZ_x * game_width / 2 + (game_width / 2)
            # 如果敌人相对于准星角度 在 以下范围 才绘制（横向）
            if (angle_DZ_x > -410 and angle_DZ_x < -310) or (angle_DZ_x > -50 and angle_DZ_x < 0):
                # 新增防御性检查
                if dis_on_space == 0:
                    continue  # 跳过零距离情况
                ratio = sub_z / dis_on_space
                ratio = max(-1.0, min(1.0, ratio))  # 限制在 [-1,1] 范围内
                angle_DW_space = math.degrees(math.asin(ratio))
                # 敌相对于我空间平面角度
                # angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                 # 确保 fov_y 是有效数值
                if not isinstance(fov_y, (int, float)):
                    raise ValueError(f"Invalid fov_y: {fov_y}")
                
                
                # 如果敌人在我上方
                if other_z >= my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y + abs(angle_DW_space)
                # 如果敌人在我下方
                elif other_z < my_z:
                    # 敌人相对于准星的角度（纵向）
                    angle_DZ_y = fov_y - abs(angle_DW_space)
                # 敌人与准星的距离（游戏中_纵向）
                dis_DZ_y = math.sin(math.radians(angle_DZ_y)) * dis_on_space  # 第三象限
                # 我与准星的距离（游戏中_纵向）
                dis_WZ_y = math.sqrt(math.pow(dis_on_space, 2) - math.pow(dis_DZ_y, 2))*0.80
                # 敌人在屏幕上的Y坐标计算
                dis_y_screen = (game_height / 2) - dis_DZ_y / dis_WZ_y * (game_height / 2)
                # 绘制方框
                drawRect(hdc, dis_x_screen + left, dis_y_screen+top+10, dis_on_space, 1, brush)
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
            dis_x_screen = dis_DZ_x / dis_WZ_x * game_width / 2 + (game_width / 2)
             # 如果敌人相对于准星角度 在 -55~50才绘制（横向）
            if angle_DZ_x > -55 and angle_DZ_x < 50:
                '''=========Y计算======='''
                # 敌相对于我空间平面角度
                angle_DW_space = math.degrees(math.asin(sub_z / dis_on_space))
                # 如果敌人在我上方
                if other_z >= my_z:
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
                dis_y_screen = (game_height / 2) - dis_DZ_y / dis_WZ_y * game_height / 2
                # 绘制方框
                drawRect(hdc, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)

# 创建Overlay窗口
overlay = OverlayWindow(game_width, game_height, draw_callback)

print("Overlay窗口已创建，开始监听游戏数据...")

win32gui.PumpMessages()  # 阻塞式消息循环


