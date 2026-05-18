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

def measure_color_change_time():
    # 正確的視窗標題字串
    target_title = "RF Switch Tool V3.0_build_2605180942"
    
    # 1. 修正連線標題，精準連接到您的 RF 工具視窗
    try:
        app = Application(backend="win32").connect(title=target_title)
    except Exception:
        print(f"找不到『{target_title}』視窗。")
        print("請確認該程式已經啟動，且視窗標題沒有打錯（包含大小寫與空格）。")
        return
        
    main_win = app.window(title=target_title)
    main_win.set_focus() # 確保視窗被帶到最上層
    
    # =========================================================================
    #【新增步驟】自動偵測並印出該視窗內所有可點擊的按鈕與控制項特徵
    print("\n" + "="*60)
    print(" 正在偵測視窗內所有可用的按鈕與控制項... (清單如下) ")
    print("="*60)
    
    main_win.print_control_identifiers() # 這行會把所有按鈕印在您的終端機上
    
    print("="*60)
    print(" 💡 請查看上方印出的清單，找出您要測試的按鈕名稱。")
    print(" 測試即將停止，請將找到的按鈕名稱更新至下方程式碼的『title』欄位中。")
    print("="*60 + "\n")
    return # 第一次執行先停在這裡，讓您看清單，確認按鈕後再繼續
    # =========================================================================
    
    # 2. 定位按鈕 (請根據上方輸出的清單，將 "點我測試" 修改為正確的按鈕名稱)
    btn = main_win.child_window(title="點我測試", control_type="Button")
    
    # 3. 取得按鈕中心點的「螢幕絕對座標」
    rect = btn.rectangle()
    center_x = (rect.left + rect.right) // 2
    center_y = (rect.top + rect.bottom) // 2
    
    hdc = win32gui.GetDC(0) 
    elapsed_times = []
    total_runs = 100
    
    print(f"開始執行 {total_runs} 次變色反應時間測試...")
    
    for i in range(1, total_runs + 1):
        initial_color = get_pixel_color(hdc, center_x, center_y)
        
        btn.click_input() 
        start_time = time.perf_counter()
        
        timeout = 2.0 
        while True:
            current_color = get_pixel_color(hdc, center_x, center_y)
            current_time = time.perf_counter()
            
            if current_color != initial_color:
                end_time = current_time
                break
                
            if (current_time - start_time) > timeout:
                end_time = None
                break
        
        if end_time:
            duration_ms = (end_time - start_time) * 1000
            elapsed_times.append(duration_ms)
            print(f"第 {i:03d} 次：變色耗時 {duration_ms:.2f} ms")
        else:
            print(f"第 {i:03d} 次：測試逾時，顏色未改變。")
        
        time.sleep(0.05) 
        
    win32gui.ReleaseDC(0, hdc)
    
    if elapsed_times:
        arr = np.array(elapsed_times)
        print("\n" + "="*30)
        print("【 100 次反應時間統計結果 】")
        print(f"成功次數: {len(elapsed_times)} / {total_runs}")
        print(f"平均反應時間 (Average): {np.mean(arr):.2f} ms")
        print(f"最快反應時間 (Min):     {np.min(arr):.2f} ms")
        print(f"最慢反應時間 (Max):     {np.max(arr):.2f} ms")
        print(f"標準差 (Standard Dev):   {np.std(arr):.2f} ms")
        print("="*30)

if __name__ == "__main__":
    measure_color_change_time()
