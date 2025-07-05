'''
client.dll+189A268  人物数组首地址
意思就是（client.dll+189A268）+8 是自己的人物地址
后续每次 +10 是其他人物地址 ，9次，因为9个其他人

x偏移 DB8
y偏移 DBC
z偏移 DC0
血量偏移 344 或 ab4

FOV_y client.dll+1A88548
FOV_X  client.dll+1A8854c

幽络源站长土拨鼠原创，仅用于学习测试
'''
import math
import pymem
import win32api
import win32gui
import win32process
import win32con

from GDIUtils import drawRect
from GDIOverlay import OverlayWindow

# Counter-Strike 2
WindowHandle = win32gui.FindWindow(None, "Counter-Strike 2")
# WindowHandle = win32gui.FindWindow(None, "反恐精英：全球攻势")

ThreadId, ProcessId = win32process.GetWindowThreadProcessId(WindowHandle)
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
ProcessHandle = pymem.process.open(ProcessId, True, PROCESS_ALL_ACCESS)
client_dll = pymem.process.module_from_name(ProcessHandle, "client.dll").lpBaseOfDll

#人物数组地址偏移
client_dll_offset_human=0x1865288
#视角地址偏移
client_dll_offset_y=0x1A794B0
client_dll_offset_x=0X1A78E24
#x坐标偏移
x_offset=0xDB8
#y坐标偏移
y_offset=0xDBC
#z坐标偏移
z_offset=0xDC0
#血量偏移
blood_offset=0x344

# DC=win32gui.GetDC(0)
DC=win32gui.GetDC(WindowHandle)
#创建DC的画板
CDC=win32gui.CreateCompatibleDC(DC)
#创建画布
bmp=win32gui.CreateCompatibleBitmap(DC,50,50)
#将画布加入画板中
win32gui.SelectObject(CDC,bmp)
brush = win32gui.CreateSolidBrush(win32api.RGB(0,0,255))



#人物数组起始地址
human_array = pymem.memory.read_longlong(ProcessHandle, client_dll + client_dll_offset_human)
my_array=0x0
my_offset=0x0
my_offset_way1=0x8
my_offset_way2=0x0
my_array_way1 = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset_way1) #自己固定偏移8或者0
my_blood_way1 = pymem.memory.read_int(ProcessHandle, my_array_way1 + blood_offset)
my_array=my_array_way1
my_offset=my_offset_way1
isEight=True
if my_blood_way1==0:
    my_array_way2 = pymem.memory.read_longlong(ProcessHandle, human_array + my_offset_way2) #自己固定偏移8或者0
    my_blood_way2 = pymem.memory.read_int(ProcessHandle, my_array_way2 + blood_offset)
    my_array = my_array_way2
    my_offset = my_offset_way2
    isEight=False

# while True:
#     # 获取窗口大小
#     rect = win32gui.GetWindowRect(WindowHandle)
    
#     # 画之前先清空画布
#     win32gui.FillRect(CDC, rect, brush)     # ...existing code...
while True:
    # 获取窗口大小
    rect = win32gui.GetWindowRect(WindowHandle)
    left, top, right, bottom = rect
    screen_width = right - left
    screen_height = bottom - top
    
    # 清空画布
    win32gui.FillRect(CDC, (0, 0, screen_width, screen_height), brush)
    
    # ...你的绘制逻辑...
    
    # 刷新到屏幕
    win32gui.BitBlt(
        DC, left, top, screen_width, screen_height,
        CDC, 0, 0, win32con.SRCCOPY
    )
    # ...existing code...
    
    # 获取窗口的左上角和右下角坐标
    left, top, right, bottom = rect
    screen_width = right - left  # 屏幕宽
    screen_height = bottom - top  # 屏幕高

    #读取自己x
    my_x=pymem.memory.read_float(ProcessHandle,my_array+x_offset)
    #读取自己y
    my_y = pymem.memory.read_float(ProcessHandle, my_array + y_offset)
    #读取自己z
    my_z = pymem.memory.read_float(ProcessHandle, my_array + z_offset)
    #读取FOV_y
    fov_y= pymem.memory.read_float(ProcessHandle, client_dll + client_dll_offset_y)
    #读取FOV_x
    fov_x= pymem.memory.read_float(ProcessHandle, client_dll + client_dll_offset_x)

    count=1
    multipliers = [0x8, 0x2] if isEight else [0x2, 0x8]
    for i in range(1, 20):
        if not isEight and i == 19:
            break
        human_offset = count * multipliers[i % 2]
        count += 1
        other_array=pymem.memory.read_longlong(ProcessHandle,human_array+my_offset+human_offset)
        #读其他人的血量
        try:
            other_blood=pymem.memory.read_int(ProcessHandle,other_array+blood_offset)
        except:
            continue
        if other_blood == 0:
            continue
        #读其他人x
        other_x=pymem.memory.read_float(ProcessHandle,other_array+x_offset)
        #读其他人y
        other_y = pymem.memory.read_float(ProcessHandle, other_array + y_offset)
        #读其他人z
        other_z = pymem.memory.read_float(ProcessHandle, other_array + z_offset)

        #敌我y差
        sub_y=other_y-my_y
        #敌我x差
        sub_x=other_x-my_x
        #敌我z差
        sub_z=other_z-my_z
        # 敌我距离_俯视
        dis_on_top = math.sqrt(math.pow(other_x - my_x, 2) + math.pow(other_y - my_y, 2))
        # 敌我空间距离
        dis_on_space=math.sqrt(math.pow(other_x-my_x,2)+math.pow(other_y-my_y,2)+math.pow(other_z-my_z,2))

        #第一象限
        if other_y>my_y and other_x>my_x:
            print("壹")
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
                drawRect(DC,CDC,dis_x_screen+left,dis_y_screen+top+10,dis_on_space,1,brush)
        #第二象限
        elif other_y>my_y and other_x<my_x:
            print("贰")
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
            print(angle_DZ_x)
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
                drawRect(DC, CDC, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)
        #第三象限（类似二象限）
        elif other_y<my_y and other_x<my_x:
            print("叁")
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
                drawRect(DC, CDC, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)
        # 第四象限
        elif other_y < my_y and other_x > my_x:
            print("肆")
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
                drawRect(DC, CDC, dis_x_screen+left, dis_y_screen+top+10, dis_on_space, 1, brush)