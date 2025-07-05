import win32gui
import win32con
import win32api
import time

class OverlayWindow:
    def __init__(self, width, height, draw_callback=None):
        self.hInstance = win32api.GetModuleHandle(None)
        className = "OverlayWindowClass"
        wndClass = win32gui.WNDCLASS()
        wndClass.lpfnWndProc = self.wndProc
        wndClass.hInstance = self.hInstance
        wndClass.lpszClassName = className
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        # wndClass.hbrBackground = win32con.COLOR_WINDOW
        wndClass.hbrBackground = 0
        self.classAtom = win32gui.RegisterClass(wndClass)
        style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
        self.hwnd = win32gui.CreateWindowEx(
            style,
            self.classAtom,
            None,
            win32con.WS_POPUP,
            0, 0, width, height,
            None, None, self.hInstance, None
        )
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0x000000, 255, win32con.LWA_COLORKEY)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        self.draw_callback = draw_callback
        self.width = width
        self.height = height

    def wndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hwnd)
            # 清空画布（黑色透明）
            brush = win32gui.CreateSolidBrush(win32api.RGB(0,0,0))
            win32gui.FillRect(hdc, (0, 0, self.width, self.height), brush)
            
            # 调用外部绘制逻辑
            if self.draw_callback:
                self.draw_callback(hdc)
            win32gui.EndPaint(hwnd, paintStruct)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def refresh(self):
        win32gui.InvalidateRect(self.hwnd, None, True)