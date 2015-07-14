import win32api, win32con, ctypes, ctypes.wintypes, threading, time, win32ui


def SetWord(Low, Hi):
    out = (Low & 0x0000FFFF) + (Hi << 16)
    return out

clicks = False
pos = SetWord(700,400)
pwin = win32ui.FindWindow(None, "Clicker Heroes")

def click(x,y):
    #win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def Click():
    global clicks
    global pos
    while(True):
        clickSpot()
        threading._sleep(.05)

def clickSpot():
    global pos
    global pwin
    pwin.PostMessage(win32con.WM_LBUTTONDOWN, 0, pos)
    pwin.PostMessage(win32con.WM_LBUTTONUP, 0, pos)


#clickSpot()

#ctypes.windll.user32.RegisterHotKey(None, 1, 0, win32con.VK_ESCAPE)

t = threading.Thread(None, Click, "clicks")
t.start()

try:
    msg = ctypes.wintypes.MSG()
    while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == win32con.WM_HOTKEY:
            clicks = not clicks
        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
        ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
finally:
    ctypes.windll.user32.UnregisterHotKey(None,1)