import cv2
import numpy as np
import pyautogui
import os
from PIL import ImageGrab
import random
import time
from utils import exist
import mss
import win32gui
import win32con
import win32api

def send_click(hwnd, x, y):
    # win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 恢复窗口
    # win32gui.SetForegroundWindow(hwnd) 
    x, y = win32gui.ScreenToClient(hwnd, (x, y))
    # print(f"发送点击到窗口：{hwnd}，位置：({x}, {y})")
    lParam = win32api.MAKELONG(x, y)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)


def loc(template_path, screen_region=None):
    current_dir = os.getcwd()
    template_path = os.path.join(current_dir, template_path)
    template_orig = cv2.imread(template_path)
    gray_template_orig = cv2.cvtColor(template_orig, cv2.COLOR_BGR2GRAY)

    # 缩放比例
    scales = [0.5, 0.7, 0.8, 0.9, 1.0]

    with mss.mss() as sct:
        if screen_region is None:
            monitor = sct.monitors[1] #副屏监控
            # screenshot_pil = ImageGrab.grab()
        else:
            monitor = {
                "left": screen_region[0],
                "top": screen_region[1],
                "width": screen_region[2] - screen_region[0],
                "height": screen_region[3] - screen_region[1]
            }
            # screenshot_pil = ImageGrab.grab(bbox=screen_region)
        screenshot_pil = sct.grab(monitor)
    screenshot_np = np.array(screenshot_pil)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    gray_screenshot = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)

    best_val = -1
    best_loc = None
    best_scale = 1.0
    best_size = (0, 0)

    for scale in scales:
        resized_template = cv2.resize(gray_template_orig, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        result = cv2.matchTemplate(gray_screenshot, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > best_val:
            best_val = max_val
            best_loc = max_loc
            best_scale = scale
            best_size = resized_template.shape[::-1]  # (w, h)

    threshold = 0.6
    if best_val >= threshold:
        print(f"窗口识别成功，位置：{best_loc}，大小：{best_size}， 匹配度：{best_val:.2f}，缩放：{best_scale:.2f}")
        return (best_loc, best_size, best_scale)
    else:
        print("未识别到窗口")
        return (None, None, None)


def beginClick(hwnd, config):
    if not exist(config.loc) or not exist(config.size):
        return False

    x, y = config.loc
    w, h = config.size

    center_x = x + (w // 2)
    center_y = y + (h // 4 * 3)

    # center_x = x + (w // 2) * 0.8
    # center_y = y + (h // 4 * 3) * 1.2 - 2

    pyautogui.click(int(center_x), int(center_y))
    # send_click(hwnd, int(center_x), int(center_y))
    # send_click(hwnd, int(-266), int(747))
    print(f"开始答题：({center_x}, {center_y})")
    return True


def clickAnswer(hwnd, answer, config):
    if not exist(config.loc) or not exist(config.size):
        return False
    
    x, y = config.loc
    w, h = config.size
    
    # h_rand = random.uniform(0, 20) * config.scale
    # w_rand = random.uniform(-20, 180) * config.scale

    ans_path = os.path.join(os.getcwd(), "img", answer.upper() + '.png')
    region = (x, y, x + w, y + h)
    loca, size, scale = loc(ans_path, region)

    if not exist(loca):
        return False

    abs_x = x + loca[0]
    abs_y = y + loca[1]

    # abs_x = x + (loca[0]) * 0.8
    # abs_y = y + (loca[1]) * 1.3
    pyautogui.click(abs_x, abs_y)
    # send_click(hwnd, int(abs_x), int(abs_y))

    return True

def continueClick(hwnd, config):
    if not exist(config.loc) or not exist(config.size):
        return False
    
    x, y = config.loc
    w, h = config.size

    h_rand = random.uniform(10, 30) * config.scale
    w_rand = random.uniform(10, 80) * config.scale

    cont_path = os.path.join(os.getcwd(), "img/continue.png")
    region = (x, y, x + w, y + h)
    cont_loc, cont_size, cont_scale = loc(cont_path, region)

    if not exist(cont_loc):
        return False


    abs_x = x + cont_loc[0] + 10
    abs_y = y + cont_loc[1] + 10

    # abs_x = x + cont_loc[0]
    # abs_y = y + cont_loc[1]

    # abs_x = x + cont_loc[0] * 0.5
    # abs_y = y + cont_loc[1] * 1.3
    print(f"继续答题：({abs_x}, {abs_y})")
    pyautogui.click(abs_x, abs_y)
    # send_click(hwnd, int(abs_x), int(abs_y))
    # send_click(hwnd, int(-395), int(792))
    time.sleep(1 + random.uniform(0, 0.5))
    pyautogui.click(abs_x, abs_y)
    # send_click(hwnd, int(abs_x), int(abs_y))
    # send_click(hwnd, int(-395), int(792))

    return True

def wrongClick(config):
    if not exist(config.loc) or not exist(config.size):
        return False

    x, y = config.loc
    w, h = config.size

    center_x = x + w // 8 * 7 + random.uniform(-5, 5)
    center_y = y + h // 3 * 2 + random.uniform(-5, 5)

    pyautogui.click(center_x, center_y)
    print(f"开始足迹：({center_x}, {center_y})")
    time.sleep(0.5 + random.uniform(0.5, 1))

    center_x = x + w // 8 + random.uniform(-5, 5)
    center_y = y + h // 7 * 6 + random.uniform(-5, 5)
    pyautogui.click(center_x, center_y)
    print(f"开始错题集：({center_x}, {center_y})")

    return True

def wrongNextClick(config):
    if not exist(config.loc) or not exist(config.size):
        return False
    
    x, y = config.loc
    w, h = config.size

    h_rand = random.uniform(4, 8) * config.scale
    w_rand = random.uniform(10, 80) * config.scale

    cont_path = os.path.join(os.getcwd(), "img/wrong_next.png")
    region = (x, y, x + w, y + h)
    cont_loc, cont_size, cont_scale = loc(cont_path, region)

    if not exist(cont_loc):
        return False

    abs_x = x + cont_loc[0] + w_rand
    abs_y = y + cont_loc[1] + h_rand
    pyautogui.click(abs_x, abs_y)

    return True

def get_color(config, position):

    x, y = config.loc

    abs_x = x + position[0]
    abs_y = y + position[1]

    # region = (abs_x, abs_y, abs_x + 2, abs_y + 2)
    # screenshot_pil = ImageGrab.grab(region)
    with mss.mss() as sct:
        monitor = {
            "left": abs_x,
            "top": abs_y,
            "width": 2,
            "height": 2
        }
        screenshot_pil = sct.grab(monitor)
       
    screenshot_np = np.array(screenshot_pil)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    b, g, r = screenshot_bgr[0, 0]
    rgb = (r, g, b)
    hex_color = '#{:02X}{:02X}{:02X}'.format(r, g, b)
    return rgb, hex_color

def chooceCorrect(config):
    x, y = config.loc
    w, h = config.size
    
    answer_list = ['A', 'B', 'C', 'D']

    loca = None
    for ans in answer_list:
        ans_path = os.path.join(os.getcwd(), "img", "corr_" + ans + '.png')
        region = (x, y, x + w, y + h)
        loca, size, scale = loc(ans_path, region)
        _, hex = get_color(config, loca)
        if hex == '#06CF99':
            return ans