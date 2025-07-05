import win32gui
import win32con
import win32api
import time

class OverlayWindow:
    def __init__(self, width, height, draw_callback=None):
        self.hInstance = win32api.GetModuleHandle(None) # 获取当前模块的实例句柄
        className = "OverlayWindowClass"
        wndClass = win32gui.WNDCLASS() # 创建窗口类
        wndClass.lpfnWndProc = self.wndProc # 设置窗口过程函数
        wndClass.hInstance = self.hInstance # 设置窗口实例句柄
        wndClass.lpszClassName = className # 设置窗口类名
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW) # 设置光标为箭头
        # wndClass.hbrBackground = win32con.COLOR_WINDOW
        wndClass.hbrBackground = 0 # 让背景不自动填充为白色
        self.classAtom = win32gui.RegisterClass(wndClass) # 注册窗口类
        style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
        self.hwnd = win32gui.CreateWindowEx(
            style,
            self.classAtom,
            None,
            win32con.WS_POPUP,
            0, 0, width, height,
            None, None, self.hInstance, None
        ) # 创建窗口
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0x000000, 255, win32con.LWA_COLORKEY) # 设置透明色为黑色
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW) # 显示窗口
        self.draw_callback = draw_callback # 设置绘制回调函数
        self.width = width # 设置窗口宽度
        self.height = height # 设置窗口高度

    def wndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hwnd) # 开始绘制
            # 清空画布（黑色透明）
            brush = win32gui.CreateSolidBrush(win32api.RGB(0,0,0)) # 创建一个黑色透明画刷
            win32gui.FillRect(hdc, (0, 0, self.width, self.height), brush) # 填充整个窗口区域
            
            # 调用外部绘制逻辑
            if self.draw_callback:
                self.draw_callback(hdc) # 调用绘制回调函数
            win32gui.EndPaint(hwnd, paintStruct) # 结束绘制
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def refresh(self):
        win32gui.InvalidateRect(self.hwnd, None, True)