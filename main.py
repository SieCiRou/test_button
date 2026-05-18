import time
import ctypes
import numpy as np
from pywinauto.application import Application
import win32gui

def get_pixel_color(hdc, x, y):
    """使用 Windows GDI API 快速獲取指定座標的 RGB 顏色"""
    color = win32gui.GetPixel(hdc, x, y)
    b = (color >> 16) & 0xff
    g = (color >> 8) & 0xff
    r = color & 0xff
    return (r, g, b)

def is_steel_blue(rgb):
    """判斷顏色是否接近 SteelBlue (標準 RGB 約為 70, 130, 180)"""
    r, g, b = rgb
    return (50 <= r <= 95) and (110 <= g <= 150) and (160 <= b <= 210)

def measure_color_change_time(total_cycles=5):
    """
    Args:
        total_cycles (int): 要測試的總輪數（次數）
    """
    target_title = "RF Switch Tool V3.0_build_2605180942"
    
    try:
        app = Application(backend="win32").connect(title=target_title)
    except Exception:
        print(f"找不到『{target_title}』視窗，請確認程式已啟動。")
        return
        
    main_win = app.window(title=target_title)
    main_win.set_focus()
    time.sleep(0.5) # 等待視窗聚焦穩定
    
    # 1. 預先取得這 8 個 CheckBox 按鈕的物件與中心點絕對座標
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

    # 紀錄所有測試時間數據 (細分為：前鈕恢復時間, 新鈕變色時間, 總耗時)
    all_records = {num: {"prev_recover": [], "curr_change": [], "total": []} for num in range(1, 9)}
    timeout_limit = 2.0  # 2秒逾時防呆
    
    print(f"\n開始執行 8 個按鈕輪流點選測試 (共設定測試 {total_cycles} 輪) ...")
    
    # 為了讓第一輪的第一個按鈕有「前一個按鈕」可以比對，先預踩第 8 個按鈕
    print("正在設定初始狀態（預點擊第 8 個按鈕）...")
    buttons[8]["obj"].click_input()
    time.sleep(0.5)
    
    for cycle in range(1, total_cycles + 1):
        print(f"\n--- 第 {cycle:03d} / {total_cycles} 輪測試 ---")
        
        for current_num in range(1, 9):
            prev_num = 8 if current_num == 1 else current_num - 1
            
            curr_btn = buttons[current_num]
            prev_btn = buttons[prev_num]
            
            # 執行真實滑鼠點擊
            curr_btn["obj"].click_input()
            start_time = time.perf_counter()
            
            prev_recover_time = None
            curr_change_time = None
            success = False
            
            # 高速輪詢監測顏色轉變
            while True:
                curr_color = get_pixel_color(hdc, curr_btn["x"], curr_btn["y"])
                prev_color = get_pixel_color(hdc, prev_btn["x"], prev_btn["y"])
                current_time = time.perf_counter()
                
                # 監測 1: 原(前)按鈕是否變回原色
                if prev_recover_time is None and (not is_steel_blue(prev_color)):
                    prev_recover_time = current_time
                
                # 監測 2: 新(當前)按鈕是否轉變為 SteelBlue 色
                if curr_change_time is None and is_steel_blue(curr_color):
                    curr_change_time = current_time
                    success = True
                    break  # 只要當前按鈕變色為 SteelBlue，即視為成功並結束輪詢
                
                if (current_time - start_time) > timeout_limit:
                    break
            
            if success:
                # 若前鈕尚未在時限內恢復，則補計當前時間以防計算出錯
                if prev_recover_time is None:
                    prev_recover_time = current_time
                    
                # 計算各階段耗時 (毫秒)
                p_recover_ms = (prev_recover_time - start_time) * 1000
                c_change_ms = (curr_change_time - start_time) * 1000
                total_ms = (curr_change_time - start_time) * 1000
                
                all_records[current_num]["prev_recover"].append(p_recover_ms)
                all_records[current_num]["curr_change"].append(c_change_ms)
                all_records[current_num]["total"].append(total_ms)
                
                print(f"  [按鈕 {current_num}] 前鈕回復: {p_recover_ms:.1f}ms | 新鈕變色: {c_change_ms:.1f}ms | 總計: {total_ms:.1f}ms")
            else:
                print(f"  [按鈕 {current_num}] 測試逾時，狀態未完全改變。")
                
            time.sleep(0.05) # 稍微緩衝，避免 UI 反應不及
            
        # 修正點：移至第一層 for 迴圈內。當每一輪 (1~8顆按鈕) 點完，立即列印截至目前為止的即時統計數據
        print("\n" + "-"*85)
        print(f" 📊 【 第 {cycle:03d} 輪結束即時累計統計結果 】")
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
            
    # 2. 釋放繪圖資源
    win32gui.ReleaseDC(0, hdc)

if __name__ == "__main__":
    measure_color_change_time(total_cycles=5)