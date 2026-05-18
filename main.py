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
    # 允許些許誤差範圍 (例如 R 在 50~90, G 在 110~150, B 在 160~200)
    return (50 <= r <= 95) and (110 <= g <= 150) and (160 <= b <= 210)

def measure_color_change_time():
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

    # 紀錄所有測試時間數據
    all_records = {num: [] for num in range(1, 9)}
    total_cycles = 100  # 總共跑 100 輪
    timeout_limit = 2.0  # 2秒逾時防呆
    
    print(f"\n 開始執行 8 個按鈕輪流點選測試 (共 {total_cycles} 輪) ...")
    
    # 為了讓第一輪的第一個按鈕有「前一個按鈕」可以比對，先預踩第 8 個按鈕
    print("正在設定初始狀態（預點擊第 8 個按鈕）...")
    buttons[8]["obj"].click_input()
    time.sleep(0.5)
    
    for cycle in range(1, total_cycles + 1):
        print(f"\n--- 🔄 第 {cycle:03d} / {total_cycles} 輪測試 ---")
        
        for current_num in range(1, 9):
            # 確定當前按鈕與前一個按鈕的編號
            prev_num = 8 if current_num == 1 else current_num - 1
            
            curr_btn = buttons[current_num]
            prev_btn = buttons[prev_num]
            
            # 取得點擊前的初始顏色狀態
            init_curr_color = get_pixel_color(hdc, curr_btn["x"], curr_btn["y"])
            init_prev_color = get_pixel_color(hdc, prev_btn["x"], prev_btn["y"])
            
            # 執行真實滑鼠點擊
            curr_btn["obj"].click_input()
            start_time = time.perf_counter()
            
            # 高速輪詢監測顏色轉變
            success = False
            while True:
                curr_color = get_pixel_color(hdc, curr_btn["x"], curr_btn["y"])
                prev_color = get_pixel_color(hdc, prev_btn["x"], prev_btn["y"])
                current_time = time.perf_counter()
                
                # 判定條件：
                # 1. 前一個按鈕已經回復原色 (不再是 steelblue，或者顏色變回跟目前按鈕點擊前一樣)
                # 2. 目前按鈕已經成功轉變成 SteelBlue 色
                if is_steel_blue(curr_color) and (not is_steel_blue(prev_color)):
                    end_time = current_time
                    success = True
                    break
                    
                if (current_time - start_time) > timeout_limit:
                    break
            
            if success:
                duration_ms = (end_time - start_time) * 1000
                all_records[current_num].append(duration_ms)
                print(f"  [按鈕 {current_num}] 變色耗時: {duration_ms:.2f} ms")
            else:
                print(f"  ❌ [按鈕 {current_num}] 測試逾時，顏色未如預期改變。")
                
            time.sleep(0.05) # 稍微緩衝，避免 UI 反應不及
            
    # 2. 釋放繪圖資源
    win32gui.ReleaseDC(0, hdc)
    
    # 3. 輸出 100 輪結束後的完整統計報告
    print("\n" + "="*50)
    print(" 📊 【 8 個按鈕變色反應時間 100 次統計結果 】")
    print("="*50)
    print(f"{'按鈕編號':<10}{'成功次數':<10}{'平均時間 (ms)':<15}{'最快 (ms)':<10}{'最慢 (ms)':<10}")
    print("-"*50)
    
    for num in range(1, 9):
        times = all_records[num]
        if times:
            arr = np.array(times)
            print(f"Btn {num:<6}{len(times):<12}{np.mean(arr):<16.2f}{np.min(arr):<12.2f}{np.max(arr):<12.2f}")
        else:
            print(f"Btn {num:<6}{0:<12}{'N/A':<16}{'N/A':<12}{'N/A':<12}")
    print("="*50)

if __name__ == "__main__":
    measure_color_change_time()
