import win32api, win32con, ctypes, ctypes.wintypes, threading, time, win32ui, win32gui
from PIL import Image

def SetWord(Low, Hi):
    out = (Low & 0x0000FFFF) + (Hi << 16)
    return out

clicks = True
click_speed = 0.02;
pos = SetWord(700,400)
pwin = win32ui.FindWindow(None, "Clicker Heroes")
hWnd = win32gui.FindWindow(None, "Clicker Heroes")

def click(x,y):
    #win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def Click():
    global clicks
    global click_speed
    global pos
    while(True):
        if clicks:
            clickSpot()
            threading._sleep(click_speed)

def clickSpot():
    global pos
    global pwin #helal la
    pwin.PostMessage(win32con.WM_LBUTTONDOWN, 0, pos)
    pwin.PostMessage(win32con.WM_LBUTTONUP, 0, pos)

# Captures the screen and returns a tuple containing
# (bits, width, height)
def captureScreen(handle):
    # Get device context for the window    
    dc = win32gui.GetWindowDC(handle)
    # Create a temporary DC compatible with our window
    dc_obj = win32ui.CreateDCFromHandle(dc)
    mem_dc = dc_obj.CreateCompatibleDC()
    # Get the client area for size calculation
    rect = win32gui.GetWindowRect(handle)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    # Create a bitmap
    bmp = win32ui.CreateBitmap()
    scr_bmp = bmp.CreateCompatibleBitmap(dc_obj, width, height);
    # Select the bitmap from memory dc.
    mem_dc.SelectObject(bmp);
    # Bit block transfer from the window context to the temporary dc
    blit_result = mem_dc.BitBlt((0, 0), (width, height),\
                                    dc_obj, (0, 0),\
                                    win32con.SRCCOPY)    
    # Result is zero if the operation fails
    if blit_result == 0:
        print win32api.GetLastError()

    # At this point bmp has the screen content
    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    return (bmpstr, bmpinfo['bmWidth'], bmpinfo['bmHeight'])

# gets a tuple (bits, width, height) and creates a PIL Image
def createPILImage(bits):
    im = Image.frombuffer('RGB',
                          (bits[1], bits[2]),
                          bits[0], 'raw', 'BGRX', 0, 1)
    return im


#clickSpot()

#ctypes.windll.user32.RegisterHotKey(None, 1, 0, win32con.VK_ESCAPE)

t = threading.Thread(None, Click, "clicks")
#t.start()

while(True):
    inp = raw_input().split()
    if inp[0] == "clk":
        clicks = not clicks
    elif inp[0] == "exit":
        break
    elif inp[0] == "set" and len(inp) > 1:
        if inp[1] == "clk":
            if len(inp) == 2:
                click_speed = 0.02
            else:
                click_speed = float(inp[2])
    elif inp[0] == "get":
        im = createPILImage(captureScreen(hWnd))
        im.save("lol.png", None)


#try:
#    msg = ctypes.wintypes.MSG()
#    while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
#        if msg.message == win32con.WM_HOTKEY:
#            clicks = not clicks
#        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
#        ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
#finally:
#    ctypes.windll.user32.UnregisterHotKey(None,1)