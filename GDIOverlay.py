import win32gui
import win32con
import win32api
import win32ui
import time

class OverlayWindow:
    def __init__(self, width, height):
        self.hInstance = win32api.GetModuleHandle(None)
        className = "OverlayWindowClass"
        wndClass = win32gui.WNDCLASS()
        wndClass.lpfnWndProc = self.wndProc
        wndClass.hInstance = self.hInstance
        wndClass.lpszClassName = className
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground = win32con.COLOR_WINDOW
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
        # 设置黑色为透明色
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0x000000, 255, win32con.LWA_COLORKEY)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def wndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hwnd)
            # 这里可以调用你的绘制逻辑
            pen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(255,0,0))
            win32gui.SelectObject(hdc, pen)
            win32gui.Rectangle(hdc, 100, 100, 300, 300)
            win32gui.EndPaint(hwnd, paintStruct)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

# if __name__ == "__main__":
#     width = win32api.GetSystemMetrics(0)
#     height = win32api.GetSystemMetrics(1)
#     overlay = OverlayWindow(width, height)
#     # 消息循环
#     while True:
#         win32gui.PumpWaitingMessages()
#         time.sleep(0.01)