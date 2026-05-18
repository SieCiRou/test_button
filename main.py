import os
import time
import ctypes
import numpy as np
from pywinauto.application import Application
import win32gui
import win32api
from openpyxl import load_workbook, Workbook

ctypes.windll.shcore.SetProcessDpiAwareness(2)

def get_pixel_color(hdc, x, y):
    color = win32gui.GetPixel(hdc, x, y)
    return (color & 0xff, (color >> 8) & 0xff, (color >> 16) & 0xff) # RGB

def is_steel_blue(rgb):
    """判定是否為選中的藍色：R低, B高，且排除過亮的白色或淡藍"""
    r, g, b = rgb
    return (r < 110) and (b > 150) and (b > r + 40)

def is_slate_gray(rgb):
    """判定是否為未選中的灰色：R,G,B 數值接近且中等亮度"""
    r, g, b = rgb
    return (80 < r < 150) and (abs(r - g) < 20) and (abs(r - b) < 20)

def log_to_excel(file_name, cycle_num, all_records):
    headers = ['輪次', '按鈕編號', '前鈕恢復時間(ms)', '新鈕變色時間(ms)', '總耗時(ms)']
    if not os.path.exists(file_name):
        wb = Workbook()
        ws = wb.active
        ws.title = "測試結果"
        ws.append(headers)
    else:
        wb = load_workbook(file_name)
        ws = wb.active

    for num in range(1, 9):
        # 取得最後一筆紀錄，若列表為空則補 0
        p = all_records[num]["prev_recover"][-1] if all_records[num]["prev_recover"] else 0
        c = all_records[num]["curr_change"][-1] if all_records[num]["curr_change"] else 0
        t = all_records[num]["total"][-1] if all_records[num]["total"] else 0
        
        ws.append([f"第 {cycle_num} 輪", f"Btn {num}", round(p, 2), round(c, 2), round(t, 2)])
    wb.save(file_name)

def measure_color_change_time(total_cycles=5, excel_file="RF_Results.xlsx"):
    target_title = "RF Switch Tool V3.0_build_2605180942"
    try:
        app = Application(backend="win32").connect(title=target_title)
    except:
        print("找不到視窗")
        return
        
    main_win = app.window(title=target_title)
    main_win.set_focus()
    hdc = win32gui.GetDC(0)
    
    buttons = {}
    print("初始化動態掃描座標...")
    for num in range(1, 9):
        btn = main_win.child_window(auto_id=f"CheckBox28_{num}", control_type="System.Windows.Forms.CheckBox")
        r = btn.rectangle()
        cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
        # 建立一個點陣列 (中心, 上, 下, 左, 右) 增加命中率，避開數字黑點
        buttons[num] = {
            "obj": btn, 
            "points": [(cx, cy-8), (cx, cy-12), (cx+10, cy-8), (cx-10, cy-8)] 
        }

    all_records = {num: {"prev_recover": [], "curr_change": [], "total": []} for num in range(1, 9)}
    
    # 初始狀態：點擊 8
    buttons[8]["obj"].click_input()
    win32api.SetCursorPos((0, 0))
    time.sleep(0.5)

    for cycle in range(1, total_cycles + 1):
        print(f"\n--- 第 {cycle} 輪 ---")
        for curr_n in range(1, 9):
            prev_n = 8 if curr_n == 1 else curr_n - 1
            curr_b, prev_b = buttons[curr_n], buttons[prev_n]

            win32api.SetCursorPos((0, 0))
            curr_b["obj"].click_input()
            t0 = time.perf_counter()
            win32api.SetCursorPos((0, 0)) 

            t_prev, t_curr = None, None
            while (time.perf_counter() - t0) < 2.0:
                now = time.perf_counter()
                
                # 多點掃描：只要其中一點符合顏色就算成功
                if t_curr is None:
                    for px, py in curr_b["points"]:
                        if is_steel_blue(get_pixel_color(hdc, px, py)):
                            t_curr = now
                            break
                
                if t_prev is None:
                    for px, py in prev_b["points"]:
                        if is_slate_gray(get_pixel_color(hdc, px, py)):
                            t_prev = now
                            break
                
                if t_curr: break # 抓到新鈕變色就跳出

            # 填充數據 (修復 IndexError)
            res_prev = (t_prev - t0)*1000 if t_prev else 0
            res_curr = (t_curr - t0)*1000 if t_curr else 0
            
            all_records[curr_n]["prev_recover"].append(res_prev)
            all_records[curr_n]["curr_change"].append(res_curr)
            all_records[curr_n]["total"].append(res_curr)

            status = "成功" if t_curr else "逾時"
            print(f"  [按鈕 {curr_n}] {status}: {res_curr:.1f}ms")
            time.sleep(0.1)
        
        log_to_excel(excel_file, cycle, all_records)
    
    win32gui.ReleaseDC(0, hdc)

if __name__ == "__main__":
    measure_color_change_time(total_cycles=15)