import time
import ctypes
import numpy as np
from pywinauto.application import Application
import win32gui
import win32api

# 確保高 DPI 螢幕真實實體座標精確
ctypes.windll.shcore.SetProcessDpiAwareness(2)

def get_pixel_color(hdc, x, y):
    """使用 Windows GDI API 快速獲取指定座標的 RGB 顏色"""
    color = win32gui.GetPixel(hdc, x, y)
    b = (color >> 16) & 0xff
    g = (color >> 8) & 0xff
    r = color & 0xff
    return (r, g, b)

def is_color_changed(base_rgb, current_rgb):
    """比對當前顏色與點擊前是否有顯著差異 (變化量 > 15 視為變色)"""
    return any(abs(b - c) > 15 for b, c in zip(base_rgb, current_rgb))

def measure_color_change_time(total_cycles=5):
    target_title = "RF Switch Tool V3.0_build_2605180942"
    
    try:
        app = Application(backend="win32").connect(title=target_title)
    except Exception:
        print(f"找不到『{target_title}』視窗，請確認程式已啟動。")
        return
        
    main_win = app.window(title=target_title)
    main_win.set_focus()
    time.sleep(0.5)
    
    buttons = {}
    hdc = win32gui.GetDC(0)
    
    print("正在初始化按鈕座標資訊...")
    for num in range(1, 9):
        auto_id = f"CheckBox28_{num}"
        try:
            btn_obj = main_win.child_window(auto_id=auto_id, control_type="System.Windows.Forms.CheckBox")
            rect = btn_obj.rectangle()
            cx = (rect.left + rect.right) // 2
            cy = (rect.top + rect.bottom) // 2
            buttons[num] = {"obj": btn_obj, "x": cx, "y": cy}
        except Exception as e:
            print(f"警告：無法定位到 {auto_id}，請檢查元件名稱是否正確。")
            win32gui.ReleaseDC(0, hdc)
            return

    all_records = {num: {"prev_recover": [], "curr_change": [], "total": []} for num in range(1, 9)}
    timeout_limit = 2.0
    
    print(f"\n開始執行 8 個按鈕輪流點選測試 (共設定測試 {total_cycles} 輪) ...")
    
    buttons[8]["obj"].click_input()
    win32api.SetCursorPos((0, 0))
    time.sleep(0.5)
    
    for cycle in range(1, total_cycles + 1):
        print(f"\n--- 第 {cycle:03d} / {total_cycles} 輪測試 ---")
        
        for current_num in range(1, 9):
            prev_num = 8 if current_num == 1 else current_num - 1
            
            curr_btn = buttons[current_num]
            prev_btn = buttons[prev_num]
            
            # 【核心修正】點擊前先截取當下的基準顏色，作為變色比對依據
            base_curr_color = get_pixel_color(hdc, curr_btn["x"], curr_btn["y"])
            base_prev_color = get_pixel_color(hdc, prev_btn["x"], prev_btn["y"])
            
            curr_btn["obj"].click_input()
            win32api.SetCursorPos((0, 0))
            
            start_time = time.perf_counter()
            prev_recover_time = None
            curr_change_time = None
            success = False
            
            while True:
                curr_color = get_pixel_color(hdc, curr_btn["x"], curr_btn["y"])
                prev_color = get_pixel_color(hdc, prev_btn["x"], prev_btn["y"])
                current_time = time.perf_counter()
                
                # 監測 1: 前按鈕是否變色（回復原狀）
                if prev_recover_time is None and is_color_changed(base_prev_color, prev_color):
                    prev_recover_time = current_time
                
                # 監測 2: 當前按鈕是否成功變色
                if curr_change_time is None and is_color_changed(base_curr_color, curr_color):
                    curr_change_time = current_time
                    success = True
                    break
                
                if (current_time - start_time) > timeout_limit:
                    break
            
            if success:
                if prev_recover_time is None:
                    prev_recover_time = current_time
                    
                p_recover_ms = (prev_recover_time - start_time) * 1000
                c_change_ms = (curr_change_time - start_time) * 1000
                total_ms = (curr_change_time - start_time) * 1000
                
                all_records[current_num]["prev_recover"].append(p_recover_ms)
                all_records[current_num]["curr_change"].append(c_change_ms)
                all_records[current_num]["total"].append(total_ms)
                
                print(f"  [按鈕 {current_num}] 前鈕回復: {p_recover_ms:.1f}ms | 新鈕變色: {c_change_ms:.1f}ms | 總計: {total_ms:.1f}ms")
            else:
                print(f"  [按鈕 {current_num}] 測試逾時，顏色未發生顯著改變。")
                
            time.sleep(0.05)
            
        print("\n" + "-"*85)
        print(f" 【 第 {cycle:03d} 輪結束即時累計統計結果 】")
        print("-"*85)
        print(f"{'按鈕編號':<10}{'成功次數':<10}{'前鈕恢復平均(ms)':<16}{'新鈕變色平均(ms)':<16}{'總耗時平均(ms)':<15}{'最快(ms)':<10}{'最慢(ms)':<10}")
        for num in range(1, 9):
            totals = all_records[num]["total"]
            p_recovers = all_records[num]["prev_recover"]
            c_changes = all_records[num]["curr_change"]
            if totals:
                print(f"Btn {num:<6}{len(totals):<12}{np.mean(p_recovers):<18.2f}{np.mean(c_changes):<18.2f}{np.mean(totals):<16.2f}{np.min(totals):<12.2f}{np.max(totals):<12.2f}")
            else:
                print(f"Btn {num:<6}{0:<12}{'N/A':<18}{'N/A':<18}{'N/A':<16}{'N/A':<12}{'N/A':<12}")
        print("="*85)
            
    win32gui.ReleaseDC(0, hdc)

if __name__ == "__main__":
    measure_color_change_time(total_cycles=3)