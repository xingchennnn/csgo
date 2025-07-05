import win32con
import win32gui
import win32api

def drawRect(hdc, x, y, dis_in_space, size, brush):
    size = 2
    width = max(1, int(20899 / dis_in_space))
    height = max(1, int(49999 / dis_in_space))
    x = int(x - width / 2)
    y = int(y - height / 4)
    # 画四条边
    win32gui.FillRect(hdc, (x, y, x + width, y + size), brush)  # 上
    win32gui.FillRect(hdc, (x, y + height, x + width, y + height + size), brush)  # 下
    win32gui.FillRect(hdc, (x, y, x + size, y + height), brush)  # 左
    win32gui.FillRect(hdc, (x + width - size, y, x + width, y + height), brush)  # 右








'''

另类思路双缓冲绘制矩形方框
dc：设备上下文对象，一般用 dc = win32gui.GetDC(0)获取即可
cdc：内存设备上下文对象，一般用 cdc = win32gui.CreateCompatibleDC(dc) 获取即可
x:要绘制的矩形的左上角点的x坐标
y:要绘制的矩形的左上角点的y坐标
size：线条的粗细(单位为像素)
brush：画刷对象 , 建议使用 brush = win32gui.CreateSolidBrush(win32api.RGB(255,0,0)) 自定义颜色
dis_in_space: 敌我空间距离
'''

'''
def drawRect(dc,cdc,x,y,dis_in_space,size,brush):
    size=2
    width=max(1, int(20899 / dis_in_space))
    height=max(1, int(49999 / dis_in_space))
    x=int(x-width/2)
    y=int(y-height/4)
    upBMP = win32gui.CreateCompatibleBitmap(dc, width, size)  # 上边框画板宽高
    win32gui.SelectObject(cdc, upBMP)
    win32gui.FillRect(cdc, (0, 0, width, size), brush)
    win32gui.BitBlt(dc, x, y, width, size, cdc, 0, 0, win32con.SRCCOPY)

    downBMP = win32gui.CreateCompatibleBitmap(dc, width, size)  # 下边框画板宽高
    win32gui.SelectObject(cdc, downBMP)
    win32gui.FillRect(cdc, (0, 0, width, size), brush)
    win32gui.BitBlt(dc, x, y + height, width, size, cdc, 0, 0, win32con.SRCCOPY)

    leftBMP = win32gui.CreateCompatibleBitmap(dc, size, height)  # 左边框画板宽高
    win32gui.SelectObject(cdc, leftBMP)
    win32gui.FillRect(cdc, (0, 0, size, height), brush)
    win32gui.BitBlt(dc, x, y, size, height, cdc, 0, 0, win32con.SRCCOPY)

    rightBMP = win32gui.CreateCompatibleBitmap(dc, size, height)  # 右边框画板宽高
    win32gui.SelectObject(cdc, rightBMP)
    win32gui.FillRect(cdc, (0, 0, size, height), brush)
    win32gui.BitBlt(dc, x + width - size, y, size, height, cdc, 0, 0, win32con.SRCCOPY)
'''   

'''
文字绘制，还有点问题
'''
def drawText(dc,cdc,dis_on_space,screen_x,screen_y):
    dis_on_space=int(dis_on_space)
    screen_y=int(screen_y)
    screen_x=int(screen_x)
    win32gui.DrawText(cdc, str(dis_on_space-50)+"米", -1, (0, 0, 40, 320), win32con.DT_BOTTOM)
    win32gui.BitBlt(dc, int(screen_x), int(screen_y), 40, 16, cdc, 0, 0, win32con.SRCCOPY)