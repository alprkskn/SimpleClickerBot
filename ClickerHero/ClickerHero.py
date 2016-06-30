import win32api, win32con, ctypes, ctypes.wintypes, threading, time, win32ui, win32gui
from PIL import Image
from itertools import izip

def SetWord(Low, Hi):
    out = (Low & 0x0000FFFF) + (Hi << 16)
    return out

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



def iter_rows(pil_image):
    """Yield tuple of pixels for each row in the image.

    From:
    http://stackoverflow.com/a/1625023/1198943

    :param PIL.Image.Image pil_image: Image to read from.

    :return: Yields rows.
    :rtype: tuple
    """
    iterator = izip(*(iter(pil_image.getdata()),) * pil_image.width)
    for row in iterator:
        yield row

# TODO: 
# Find the top-left-most non-alpha pixel for the sub-image
# Use that as ann offset for the control-frame
# And follow an approach similar to the one below with opacity and similarity thresholds.


def find_subimage(large_image, subimg_path):
    """
       From:
       http://stackoverflow.com/a/36829325
    """
    """Find subimg coords in large_image. Strip transparency for simplicity.

    :param PIL.Image.Image large_image: Screen shot to search through.
    :param str subimg_path: Path to subimage file.

    :return: X and Y coordinates of top-left corner of subimage.
    :rtype: tuple
    """
    # Load subimage into memory.
    with Image.open(subimg_path) as rgba, rgba.convert(mode='RGB') as subimg:
        si_pixels = list(rgba.getdata())
        si_width = subimg.width
        si_height = subimg.height

    # Find the first row with at least one opaque pixel
    y_offset = 0
    while y_offset < si_height:
        si_first_row = tuple(si_pixels[y_offset*si_width:(y_offset+1)*si_width])
        si_first_row_set = set(filter(lambda a : (a[3] > 210) if len(a) > 3 else True, si_first_row))
        si_first_pixel = si_first_row[0]
        if si_first_row_set:
            break
        y_offset += 1

    # Look for first row in large_image, then crop and compare pixel arrays.
    for y_pos, row in enumerate(iter_rows(large_image)):
        print y_pos, "out of", large_image.height - 1

        # filter the sub_image's first row applying pixel comparison.
        a = filter(lambda px : not any([pix_cmp(bg, px) for bg in set(row)]), si_first_row_set)
        #if si_first_row_set - set(row):
        if a:
            continue  # Some pixels not found.
        for x_pos in range(large_image.width - si_width + 1):
            if not pix_cmp(row[x_pos], si_first_pixel):
                continue  # Pixel does not match.
            print "First row match %"
            if not matchLists(row[x_pos:x_pos + si_width], si_first_row, 0.8, 0.8):
                continue  # First row does not match.
            box = x_pos, y_pos - y_offset, x_pos + si_width, y_pos - y_offset + si_height
            with large_image.crop(box) as cropped:
                if matchLists(list(cropped.getdata()), si_pixels, 0.8, 0.8):
                    # We found our match!
                    return x_pos, y_pos

def matchLists(image, template, opacity_threshold = 1.0, similarity_threshold = 1.0):
    """ Compare two pixel lists. Instead of a direct subtraction,
        this method applies an opacity and similarity treshold.

        :param Left-hand side
        :param Right-hand side
        :param Alpha threshold for the pixels of the template which will be taken into account for comparison. (From 0.0 to 1.0)
        :param Similarity threshold for lists to be accepted as matching. (From 0.0 to 1.0)

        :return: True if two lists match within the given thresholds. False if not.
        :rtype : bool
    """
    pass_threshold = int(len(template) * similarity_threshold)
    match_count = 0
    for i in range(len(template)):
        px_img = image[i]
        px_tmp = template[i]
        alpha_tmp = (px_tmp[3] / 256.0) if len(px_tmp) > 3 else 1
        match_count += int((alpha_tmp < opacity_threshold) or (pix_cmp(px_img, px_tmp)))
        
    print (float(match_count) / pass_threshold) * 100, "%"
    return match_count >= pass_threshold

def pix_cmp(background, template):
    if len(template) == 4:
        # template has alpha channel
        oneMinusAlpha = 255 - template[3] #1 - (template[3] / 256.0)
        #dr = abs(background[0] - template[0]) / float(template[0])
        #dg = abs(background[1] - template[1]) / float(template[1])
        #db = abs(background[2] - template[2]) / float(template[2])
        return (abs(background[0] - template[0]) <= oneMinusAlpha)\
                and (abs(background[1] - template[1]) <= oneMinusAlpha)\
                and (abs(background[2] - template[2]) <= oneMinusAlpha)
    else:
        return background[:3] == template

if __name__ == "__main__":
    clicks = True
    click_speed = 0.02;
    pos = SetWord(700,400)
    pwin = win32ui.FindWindow(None, "Clicker Heroes")
    hWnd = win32gui.FindWindow(None, "Clicker Heroes")


    t = threading.Thread(None, Click, "clicks")
    #t.start()

    with Image.open("test_cases/sample_2.bmp") as bmp, bmp.convert(mode='RGB') as large_img:
        print find_subimage(large_img, "test_cases/click_thingie.png")


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
